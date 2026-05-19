"""
SAP Cloud ERP Business Case Calculator — Admin Page
Configure Improvement % per Value Driver + User Productivity.
"""
from __future__ import annotations

import streamlit as st
from storage import load_settings, save_settings, BUSINESS_AREAS
from calculator import VALUE_DRIVERS
from industry_data import get_benchmark, get_cogs_pct

st.set_page_config(
    page_title="Admin — Value Driver Config",
    page_icon="⚙️",
    layout="wide",
)

# ── Password gate ─────────────────────────────────────────────────────────────
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    st.markdown(
        "<h2 style='text-align:center; padding-top:80px;'>⚙️ Admin Access</h2>",
        unsafe_allow_html=True,
    )
    col_l, col_c, col_r = st.columns([2, 2, 2])
    with col_c:
        pwd = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Enter admin password")
        if st.button("Login", type="primary", use_container_width=True):
            correct = st.secrets.get("admin", {}).get("password", "")
            if pwd == correct:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    st.stop()

# ── Admin UI ──────────────────────────────────────────────────────────────────
st.title("⚙️ Admin: Value Driver Configuration")
st.caption("Adjust the Improvement % applied to each Value Driver's industry benchmark baseline.")

if st.button("🔒 Logout", type="secondary"):
    st.session_state.admin_authenticated = False
    st.rerun()

st.divider()

settings = load_settings()
saved_overrides: dict[str, float] = settings.get("improvement_overrides", {})

# ── User Productivity ─────────────────────────────────────────────────────────
st.subheader("User Productivity")
productivity_pct = st.number_input(
    "Improvement % applied to (Number of Users × Avg. Annual Salary)",
    min_value=0.0,
    max_value=100.0,
    value=float(settings.get("productivity_pct", 10.0)),
    step=0.5,
    format="%.1f",
)

st.divider()

# ── Discount Rate ─────────────────────────────────────────────────────────────
st.subheader("Discount Rate")
discount_rate = st.number_input(
    "Discount Rate % (used for NPV calculation)",
    min_value=0.0,
    max_value=100.0,
    value=float(settings.get("discount_rate_pct", 14.0)),
    step=0.5,
    format="%.1f",
)

st.divider()

# ── Value Drivers by Business Area ────────────────────────────────────────────
st.subheader("Value Drivers")
st.caption("Improvement % is applied on top of the industry benchmark baseline. Baseline values are determined automatically by industry and maturity selection.")

col_prev_ind, col_prev_mat = st.columns(2)
with col_prev_ind:
    from storage import INDUSTRIES
    preview_industry = st.selectbox(
        "Preview Industry",
        options=INDUSTRIES,
        index=INDUSTRIES.index("High Tech"),
        help="Select an industry to preview baseline formula values",
        key="admin_preview_industry",
    )
with col_prev_mat:
    preview_maturity_label = st.selectbox(
        "Preview Maturity",
        options=["Leader", "Average", "Laggard"],
        index=1,
        key="admin_preview_maturity",
    )
    preview_maturity = {"Leader": "top", "Average": "average", "Laggard": "bottom"}[preview_maturity_label]

preview_cogs_pct = get_cogs_pct(preview_industry, preview_maturity)

def _baseline_formula(vd: dict, industry: str, maturity: str, cogs_pct: float) -> str:
    benchmark = get_benchmark(vd["benchmark_kpi"], industry, maturity)
    btype = vd["baseline_type"]
    if benchmark is None:
        return "N/A for this industry"
    if btype == "revenue_pct":
        return f"Revenue × {benchmark:.1f}%"
    elif btype == "cogs_pct":
        return f"Revenue × {cogs_pct:.1f}% (COGS) × {benchmark:.1f}%"
    elif btype == "days_revenue":
        return f"Revenue / 365 × {benchmark:.1f} days"
    elif btype == "days_cogs":
        return f"Revenue × {cogs_pct:.1f}% (COGS) / 365 × {benchmark:.1f} days"
    elif btype == "direct_spend_pct":
        from industry_data import get_mfg_cost_pct, get_direct_spend_params
        mfg_pct = get_mfg_cost_pct(industry, maturity)
        if mfg_pct is None:
            return "N/A for this industry"
        params = get_direct_spend_params(maturity)
        return (f"Revenue × {mfg_pct:.1f}% (Mfg) × {benchmark:.1f}% (Direct Mat.) "
                f"× {params['spend_under_mgmt_pct']:.0f}% (Under Mgmt) "
                f"× {params['sourcing_savings_rate_pct']:.1f}% (Savings Rate)")
    return vd["baseline_type"]

updated_overrides: dict[str, float] = {}

for area in BUSINESS_AREAS:
    area_vds = [vd for vd in VALUE_DRIVERS if vd["area"] == area]
    if not area_vds:
        continue

    st.markdown(f"**{area}**")
    col_headers = st.columns([4, 2, 4])
    col_headers[0].markdown("<small>Value Driver</small>", unsafe_allow_html=True)
    col_headers[1].markdown("<small>Improvement %</small>", unsafe_allow_html=True)
    col_headers[2].markdown("<small>Baseline Formula</small>", unsafe_allow_html=True)

    for vd in area_vds:
        c1, c2, c3 = st.columns([4, 2, 4])
        with c1:
            st.markdown(f"<small>{vd['name']}</small>", unsafe_allow_html=True)
        with c2:
            val = st.number_input(
                "imp",
                min_value=0.0,
                max_value=100.0,
                value=float(saved_overrides.get(vd["name"], vd["improvement_pct"])),
                step=0.5,
                format="%.1f",
                key=f"imp_{vd['name']}",
                label_visibility="collapsed",
            )
            updated_overrides[vd["name"]] = val
        with c3:
            formula = _baseline_formula(vd, preview_industry, preview_maturity, preview_cogs_pct)
            st.markdown(
                f"<small style='color:gray'>{formula}</small>",
                unsafe_allow_html=True,
            )

    st.divider()

# ── Benefit Realization Schedule ──────────────────────────────────────────────
st.subheader("Benefit Realization Schedule")
st.caption("Set the % of annual benefit realized each year. Payback and 5-year totals will reflect these rates.")

DEFAULT_REALIZATION = [100.0, 100.0, 100.0, 100.0, 100.0]
saved_recurring = settings.get("realization_recurring", DEFAULT_REALIZATION)
saved_onetime   = settings.get("realization_onetime",   DEFAULT_REALIZATION)

rec_cols = st.columns(5)
one_cols = st.columns(5)

st.markdown("<small><b>Annual Recurring Benefit (%)</b></small>", unsafe_allow_html=True)
rec_vals = []
rec_cols = st.columns(5)
for i in range(5):
    v = rec_cols[i].number_input(
        f"Year {i+1}",
        min_value=0.0, max_value=200.0,
        value=float(saved_recurring[i]) if i < len(saved_recurring) else 100.0,
        step=5.0, format="%.1f",
        key=f"real_rec_{i}",
    )
    rec_vals.append(v)

st.markdown("<small><b>One-time Benefit (%)</b></small>", unsafe_allow_html=True)
one_vals = []
one_cols = st.columns(5)
for i in range(5):
    v = one_cols[i].number_input(
        f"Year {i+1}",
        min_value=0.0, max_value=200.0,
        value=float(saved_onetime[i]) if i < len(saved_onetime) else 100.0,
        step=5.0, format="%.1f",
        key=f"real_one_{i}",
    )
    one_vals.append(v)

st.divider()

# ── Save ──────────────────────────────────────────────────────────────────────
if st.button("💾 Save Configuration", type="primary"):
    save_settings({
        "productivity_pct": productivity_pct,
        "discount_rate_pct": discount_rate,
        "improvement_overrides": updated_overrides,
        "realization_recurring": rec_vals,
        "realization_onetime": one_vals,
    })
    st.success("✅ Configuration saved successfully!")
    st.rerun()
