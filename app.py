"""
SAP Cloud ERP Business Case Calculator — Main (User) Page
"""
from __future__ import annotations
import re

import streamlit as st
from storage import load_config, load_settings, BUSINESS_AREAS, INDUSTRIES
from calculator import calculate_benefits, find_scalar
from sheets import log_opportunity

APAC_CURRENCIES = {
    "AUD – Australian Dollar":  ("AUD", "A$"),
    "CNY – Chinese Yuan":       ("CNY", "¥"),
    "HKD – Hong Kong Dollar":   ("HKD", "HK$"),
    "IDR – Indonesian Rupiah":  ("IDR", "Rp"),
    "INR – Indian Rupee":       ("INR", "₹"),
    "JPY – Japanese Yen":       ("JPY", "¥"),
    "KRW – Korean Won":         ("KRW", "₩"),
    "MYR – Malaysian Ringgit":  ("MYR", "RM"),
    "NZD – New Zealand Dollar": ("NZD", "NZ$"),
    "PHP – Philippine Peso":    ("PHP", "₱"),
    "PKR – Pakistani Rupee":    ("PKR", "₨"),
    "SGD – Singapore Dollar":   ("SGD", "S$"),
    "THB – Thai Baht":          ("THB", "฿"),
    "TWD – Taiwan Dollar":      ("TWD", "NT$"),
    "VND – Vietnamese Dong":    ("VND", "₫"),
}

# Default annual salary per currency code (from country salary table)
DEFAULT_SALARY: dict[str, float] = {
    "AUD": 105_000,
    "CNY": 198_000,
    "HKD": 395_000,
    "IDR": 155_000_000,
    "INR": 1_320_000,
    "JPY": 6_600_000,
    "KRW": 53_000_000,
    "MYR": 99_000,
    "NZD": 97_000,
    "PHP": 550_000,
    "PKR": 2_650_000,
    "SGD": 64_000,
    "THB": 605_000,
    "TWD": 990_000,
    "VND": 330_000_000,
}

OPP_PATTERN = re.compile(r"^\d{9}$")


def fmt(value: float, symbol: str) -> str:
    escaped = symbol.replace("$", r"\$")
    return f"{escaped}{value:,.0f}"


def parse_number(raw: str) -> float | None:
    """Parse a comma-formatted number string into float. Returns None if empty or invalid."""
    cleaned = raw.replace(",", "").replace(" ", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def number_input_text(label: str, key: str, symbol: str, placeholder: str = "e.g. 1,000,000", help: str = "") -> float | None:
    """Text input that accepts comma-formatted numbers and reformats on entry."""
    # Reformat the stored value with commas after each entry
    if key in st.session_state:
        raw = st.session_state[key]
        parsed = parse_number(str(raw))
        if parsed is not None:
            formatted = f"{parsed:,.0f}"
            if str(raw) != formatted:
                st.session_state[key] = formatted

    raw = st.text_input(label, key=key, placeholder=placeholder, help=help)
    if not raw:
        return None
    value = parse_number(raw)
    if value is None:
        st.error(f"{label}: please enter a valid number (e.g. 1,000,000)")
        return None
    return value


st.set_page_config(
    page_title="SAP Cloud ERP Business Case Calculator",
    page_icon="💼",
    layout="wide",
)

# ── Landing page: Opportunity Number gate ─────────────────────────────────────
if "opp_number" not in st.session_state:
    st.session_state.opp_number = None

if st.session_state.opp_number is None:
    st.markdown(
        "<h1 style='text-align:center; padding-top: 80px;'>💼 SAP Cloud ERP<br>Business Case Calculator</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:gray;'>Please enter your Opportunity Number to continue.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([2, 2, 2])
    with col_c:
        opp_input = st.text_input(
            "Opportunity Number",
            placeholder="e.g. 123456789",
            max_chars=9,
            label_visibility="collapsed",
        )
        submitted = st.button("Continue →", type="primary", use_container_width=True)

    if submitted:
        if OPP_PATTERN.match(opp_input.strip()):
            st.session_state.opp_number = opp_input.strip()
            log_opportunity(st.session_state.opp_number)
            st.rerun()
        else:
            st.error("Opportunity Number must be exactly 9 digits.")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("💼 SAP Cloud ERP Business Case Calculator")
st.caption(
    f"Opportunity: **{st.session_state.opp_number}**  |  "
    "Estimate the financial value of SAP Cloud ERP adoption for your customer."
)

if st.button("← Change Opportunity", type="secondary"):
    st.session_state.opp_number = None
    st.rerun()

st.divider()

# ── Currency selector ─────────────────────────────────────────────────────────
currency_label = st.selectbox(
    "Currency",
    options=list(APAC_CURRENCIES.keys()),
    index=0,
    help="Select the currency for all monetary inputs and outputs",
)
currency_code, currency_symbol = APAC_CURRENCIES[currency_label]

# ── Industry selector ─────────────────────────────────────────────────────────
col_ind, col_mat = st.columns(2)
with col_ind:
    industry = st.selectbox(
        "Industry",
        options=INDUSTRIES,
        index=None,
        placeholder="Select customer industry...",
        help="Industry selection will determine value driver baselines",
    )
with col_mat:
    maturity_label = st.selectbox(
        "Operational Maturity",
        options=["Leader", "Average", "Laggard"],
        index=1,
        help="Determines which benchmark tier (Top 25% / Average / Bottom 25%) is used as baseline",
    )
    maturity = {"Leader": "top", "Average": "average", "Laggard": "bottom"}[maturity_label]

st.divider()

# ── Inputs ────────────────────────────────────────────────────────────────────
st.subheader("Customer Profile")

col1, col2 = st.columns(2)
with col1:
    revenue = number_input_text(
        f"Annual Revenue ({currency_code})",
        key="revenue",
        symbol=currency_symbol,
        help="Customer's total annual revenue",
    )
    impl_cost = number_input_text(
        f"Implementation Cost ({currency_code})",
        key="impl_cost",
        symbol=currency_symbol,
        help="One-time implementation / professional services cost",
    )

with col2:
    num_users = st.number_input(
        "Number of Users",
        min_value=1,
        value=None,
        placeholder="Enter number",
        step=50,
    )
    select_all = st.checkbox("Select All Business Areas", value=False)
    selected_areas = st.multiselect(
        "Business Areas in Scope",
        options=BUSINESS_AREAS,
        default=BUSINESS_AREAS if select_all else [],
        help="Select the functional areas this customer will adopt",
        disabled=select_all,
    )

st.subheader(f"SAP Subscription Cost / ACV by Year ({currency_code})")
st.caption("Enter Year 1 — Years 2–5 will auto-fill with the same value and can be edited individually.")

acv_cols = st.columns(5)

# Reformat ACV Year 1
if "acv_y1" in st.session_state:
    parsed = parse_number(str(st.session_state["acv_y1"]))
    if parsed is not None:
        formatted = f"{parsed:,.0f}"
        if str(st.session_state["acv_y1"]) != formatted:
            st.session_state["acv_y1"] = formatted

acv_y1_raw = acv_cols[0].text_input("Year 1", key="acv_y1", placeholder="e.g. 1,000,000")
acv_y1 = parse_number(acv_y1_raw) if acv_y1_raw else None

# Auto-fill Years 2-5 from Year 1 when Year 1 changes
if acv_y1 is not None and st.session_state.get("_last_acv_y1") != acv_y1:
    for i in range(2, 6):
        st.session_state[f"acv_y{i}"] = f"{acv_y1:,.0f}"
    st.session_state["_last_acv_y1"] = acv_y1

acv_by_year = [acv_y1 or 0.0]
for i in range(1, 5):
    # Reformat ACV Year i+1
    key = f"acv_y{i + 1}"
    if key in st.session_state:
        parsed = parse_number(str(st.session_state[key]))
        if parsed is not None:
            formatted = f"{parsed:,.0f}"
            if str(st.session_state[key]) != formatted:
                st.session_state[key] = formatted
    raw = acv_cols[i].text_input(f"Year {i + 1}", key=key, placeholder="e.g. 1,000,000")
    val = parse_number(raw) if raw else None
    acv_by_year.append(val if val is not None else 0.0)

st.divider()

# ── Validation ────────────────────────────────────────────────────────────────
_ready = True
if not selected_areas:
    st.warning("Please select at least one Business Area.")
    _ready = False
if revenue is None or impl_cost is None or num_users is None:
    st.info("Please fill in all customer profile fields above to see the results.")
    _ready = False
if industry is None:
    st.info("Please select a customer industry above to see the results.")
    _ready = False

# ── Calculate button ──────────────────────────────────────────────────────────
if _ready:
    _calc_key = (
        revenue, impl_cost, num_users, tuple(acv_by_year),
        currency_code, industry, maturity, tuple(selected_areas),
    )
    if st.session_state.get("_calc_key") != _calc_key and "results" in st.session_state:
        st.info("Inputs have changed. Click **Calculate** to refresh results.")

    if st.button("🔍 Calculate Business Case", type="primary", use_container_width=True):
        avg_salary = float(DEFAULT_SALARY.get(currency_code, 0))
        _settings = load_settings()
        productivity_pct      = float(_settings.get("productivity_pct", 10.0))
        improvement_overrides = _settings.get("improvement_overrides", {})
        realization_recurring = _settings.get("realization_recurring", [100.0] * 5)
        realization_onetime   = _settings.get("realization_onetime",   [100.0] * 5)
        discount_rate_pct     = float(_settings.get("discount_rate_pct", 14.0))

        with st.spinner("Optimising value drivers..."):
            scalar_step = float(_settings.get("scalar_step", 0.05))
            scalar = find_scalar(
                revenue, acv_by_year, impl_cost, num_users, avg_salary,
                productivity_pct, selected_areas, industry, maturity,
                improvement_overrides=improvement_overrides,
                realization_recurring=realization_recurring,
                realization_onetime=realization_onetime,
                discount_rate_pct=discount_rate_pct,
                scalar_step=scalar_step,
            )
            results = calculate_benefits(
                revenue, acv_by_year, impl_cost, num_users, avg_salary,
                productivity_pct, selected_areas, industry, maturity,
                improvement_overrides=improvement_overrides,
                realization_recurring=realization_recurring,
                realization_onetime=realization_onetime,
                discount_rate_pct=discount_rate_pct,
                scalar=scalar,
            )

        st.session_state["results"]              = results
        st.session_state["realization_recurring"] = realization_recurring
        st.session_state["realization_onetime"]   = realization_onetime
        st.session_state["discount_rate_pct"]     = discount_rate_pct
        st.session_state["currency_symbol"]       = currency_symbol
        st.session_state["currency_code"]         = currency_code
        st.session_state["industry"]              = industry
        st.session_state["maturity_label"]        = maturity_label
        st.session_state["_calc_key"]             = _calc_key

# ── Results (shown only after Calculate) ─────────────────────────────────────
if "results" in st.session_state:
    results              = st.session_state["results"]
    realization_recurring = st.session_state["realization_recurring"]
    realization_onetime   = st.session_state["realization_onetime"]
    discount_rate_pct     = st.session_state["discount_rate_pct"]
    _sym                 = st.session_state["currency_symbol"]
    _code                = st.session_state["currency_code"]
    _industry            = st.session_state["industry"]
    _maturity_label      = st.session_state["maturity_label"]

    # ── KPI Summary ───────────────────────────────────────────────────────────
    st.subheader("Business Case Summary (5-Year Horizon)")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Annual Recurring Benefit", fmt(results["annual_recurring_benefit"], _sym),
              help="Full-run annual benefit from recurring value drivers (before realization rate)")
    k2.metric("One-time Benefit", fmt(results["one_time_benefit"], _sym),
              help="Working capital release from DSO, DPO, DII improvements (before realization rate)")
    k3.metric("5-Year Total Benefit", fmt(results["five_year_benefit"], _sym),
              help="Sum of year-by-year benefits with realization rates applied (Recurring + One-time)")
    k4.metric("5-Year Net Benefit", fmt(results["net_benefit"], _sym),
              help="5-Year Total Benefit − 5-Year Total Cost")

    k5, k6, k7, k8 = st.columns(4)
    k5.metric(
        f"5-Year NPV ({results['discount_rate_pct']:.0f}% discount)",
        fmt(results["npv"], _sym),
        help=f"Net Present Value discounted at {results['discount_rate_pct']:.0f}% per year",
    )
    k6.metric(
        "NPV-based ROI",
        f"{results['npv_roi_pct']:.0f}%",
        help="(5-Year NPV / 5-Year Total Cost) × 100",
    )
    irr = results.get("irr_pct")
    k7.metric(
        "IRR",
        f"{irr:.0f}%" if irr is not None else "N/A",
        help="Internal Rate of Return — discount rate at which NPV = 0",
    )
    k8.metric("Payback Period", f"{results['payback_years']:.1f} yrs",
              help="Year when cumulative benefit (recurring + one-time, with realization rates) exceeds total cost")

    k9, k10, _, __ = st.columns(4)
    k9.metric("  ↳ Subscription", fmt(results["five_year_subscription"], _sym))
    k10.metric("  ↳ Implementation", fmt(results["impl_cost"], _sym))

    st.divider()

    # ── Detailed Breakdown ────────────────────────────────────────────────────
    st.subheader("Value Driver Breakdown by Business Area")

    for area, data in results["by_area"].items():
        with st.expander(
            f"**{area}**  —  Recurring: {fmt(data['subtotal_recurring'], _sym)} / One-time: {fmt(data['subtotal_one_time'], _sym)}",
            expanded=False,
        ):
            rows = []
            for d in data["drivers"]:
                row = {
                    "Value Driver": d["name"],
                    "Type": "One-time" if d["one_time"] else "Recurring",
                    f"Baseline ({_code})": fmt(d["baseline"], _sym),
                    "Improvement %": f"{d['improvement_pct']:.1f}%",
                    f"Benefit ({_code})": fmt(d["benefit"], _sym),
                }
                if d["baseline_type"] == "direct_spend_pct":
                    row["Spend Under Mgmt %"] = f"{d['spend_under_mgmt_pct']:.1f}%"
                    row["Sourcing Savings Rate %"] = f"{d['sourcing_savings_rate_pct']:.1f}%"
                rows.append(row)
            st.table(rows)

    # ── User Productivity ─────────────────────────────────────────────────────
    prod = results["productivity"]
    with st.expander(
        f"**User Productivity**  —  Annual Benefit: {fmt(prod['annual_benefit'], _sym)}",
        expanded=False,
    ):
        st.table([{
            "Value Driver": "User Productivity Improvement",
            "Users": f"{prod['num_users']:,}",
            f"Avg. Annual Salary ({_code})": fmt(prod["avg_salary"], _sym),
            f"Total Salary Baseline ({_code})": fmt(prod["baseline"], _sym),
            "Benefit %": f"{prod['benefit_pct']:.1f}%",
            f"Annual Benefit ({_code})": fmt(prod["annual_benefit"], _sym),
        }])

    st.divider()

    # ── Export ────────────────────────────────────────────────────────────────
    st.subheader("Export")
    customer_name = st.text_input(
        "Customer Name",
        placeholder="e.g. Acme Corp",
        key="customer_name",
    )

    col_png, col_pe = st.columns(2)

    with col_png:
        if st.button("📊 Download Value Tree Image", type="primary", use_container_width=True):
            from export_image import generate_value_tree_png
            with st.spinner("Generating image..."):
                png_bytes = generate_value_tree_png(
                    results=results,
                    customer_name=customer_name or "Customer",
                    currency_symbol=_sym,
                    currency_code=_code,
                    industry=_industry,
                    maturity_label=_maturity_label,
                )
            st.download_button(
                label="💾 Save PNG",
                data=png_bytes,
                file_name=f"ValueTree_{(customer_name or 'Customer').replace(' ', '_')}.png",
                mime="image/png",
                use_container_width=True,
            )

    with col_pe:
        if st.button("📈 Download Project Economics Image", type="primary", use_container_width=True):
            from export_image import generate_project_economics_png
            with st.spinner("Generating image..."):
                pe_bytes = generate_project_economics_png(
                    results=results,
                    currency_symbol=_sym,
                    currency_code=_code,
                    realization_recurring=realization_recurring,
                    realization_onetime=realization_onetime,
                    discount_rate_pct=discount_rate_pct,
                )
            st.download_button(
                label="💾 Save PNG",
                data=pe_bytes,
                file_name=f"ProjectEconomics_{(customer_name or 'Customer').replace(' ', '_')}.png",
                mime="image/png",
                use_container_width=True,
            )

    if st.button("📑 Download PowerPoint (Value Tree + Project Economics)", type="primary", use_container_width=True):
        from export_pptx import generate_pptx
        with st.spinner("Generating PowerPoint..."):
            pptx_bytes = generate_pptx(
                results=results,
                customer_name=customer_name or "Customer",
                currency_symbol=_sym,
                currency_code=_code,
                industry=_industry,
                maturity_label=_maturity_label,
                realization_recurring=realization_recurring,
                realization_onetime=realization_onetime,
                discount_rate_pct=discount_rate_pct,
            )
        st.download_button(
            label="💾 Save PPTX",
            data=pptx_bytes,
            file_name=f"BusinessCase_{(customer_name or 'Customer').replace(' ', '_')}.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )

st.caption("Go to the **Admin** page (sidebar) to configure Value Drivers per Business Area.")
