"""
Image export for Value Tree — renders a PNG matching SAP template colors.
"""
from __future__ import annotations
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.family"] = "Helvetica Neue"

C_NAVY   = "#00144A"
C_BLUE   = "#0070F2"
C_REC    = "#D1EFFF"
C_ONE    = "#E2D8FF"
C_WHITE  = "#FFFFFF"
C_BLACK  = "#000000"
C_GRAY   = "#666666"
C_LGRAY  = "#F4F6FA"
C_BORDER = "#C8D4E8"


def _fmt_m(value: float, symbol: str) -> str:
    m = value / 1_000_000
    if abs(m) >= 1000:
        return f"{symbol}{m/1000:,.1f}B"
    elif abs(m) >= 1:
        return f"{symbol}{m:,.1f}M"
    elif abs(value) >= 1000:
        return f"{symbol}{value/1000:,.1f}K"
    else:
        return f"{symbol}{value:,.0f}"


def _rect(ax, x, y, w, h, color, radius=0.008, edgecolor=None, lw=0.6, zorder=2):
    ec = edgecolor or color
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=color, edgecolor=ec, linewidth=lw, zorder=zorder,
        transform=ax.transData, clip_on=False,
    ))


def generate_value_tree_png(
    results: dict,
    customer_name: str,
    currency_symbol: str,
    currency_code: str,
    industry: str,
    maturity_label: str,
) -> bytes:

    areas_layout = [
        ["Asset Management", "Finance", "Manufacturing", "Sales"],
        ["Procurement", "R&D", "Supply Chain"],
    ]

    # ── 캔버스: 작게 잡고 dpi 높여서 글자 비율 크게 ──────────────────────────
    FIG_W, FIG_H = 13.0, 7.5
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor(C_LGRAY)
    ax.set_facecolor(C_LGRAY)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # ── 헤더 ────────────────────────────────────────────────────────────────────
    HH = 0.075
    _rect(ax, 0, 1 - HH, 1, HH, C_NAVY, radius=0, zorder=3)
    ax.text(0.012, 1 - HH/2, f"Value Potential for {customer_name}",
            color=C_WHITE, fontsize=24, fontweight="bold", va="center", ha="left", zorder=4)
    ax.text(0.988, 1 - HH/2,
            f"Currency: {currency_code}   |   Industry: {industry}",
            color="#A8C4E8", fontsize=12, va="center", ha="right", zorder=4)

    # ── 토탈 바 ──────────────────────────────────────────────────────────────────
    total_rec = results["annual_recurring_benefit"]
    total_one = results["one_time_benefit"]

    TY = 1 - HH - 0.005
    TH = 0.068
    _rect(ax, 0.005, TY - TH, 0.990, TH, C_WHITE, radius=0.005, edgecolor=C_BORDER, lw=0.8, zorder=2)

    mid_y = TY - TH/2
    chip_h = 0.032
    _rect(ax, 0.280, mid_y - chip_h/2, 0.013, chip_h, C_REC, radius=0.003, edgecolor=C_BORDER, lw=0.5)
    ax.text(0.297, mid_y, f"Recurring:  {_fmt_m(total_rec, currency_symbol)}",
            color=C_BLACK, fontsize=13, fontweight="bold", va="center", ha="left", zorder=3)
    _rect(ax, 0.620, mid_y - chip_h/2, 0.013, chip_h, C_ONE, radius=0.003, edgecolor=C_BORDER, lw=0.5)
    ax.text(0.637, mid_y, f"One-time:  {_fmt_m(total_one, currency_symbol)}",
            color=C_BLACK, fontsize=13, fontweight="bold", va="center", ha="left", zorder=3)

    # ── 그리드 ───────────────────────────────────────────────────────────────────
    M       = 0.005
    GTOP    = TY - TH - 0.005
    GBOT    = 0.008
    RGAP    = 0.007
    ROW_H   = (GTOP - GBOT - RGAP) / 2
    CGAP    = 0.006
    BP      = 0.007

    for ri, row_areas in enumerate(areas_layout):
        n      = len(row_areas)
        col_w  = (1 - M*2 - CGAP*(n-1)) / n
        rtop   = GTOP - ri*(ROW_H + RGAP)
        rbot   = rtop - ROW_H

        for ci, area in enumerate(row_areas):
            x0 = M + ci*(col_w + CGAP)
            x1 = x0 + col_w
            data = results["by_area"].get(area)
            if not data:
                continue

            rec     = data["subtotal_recurring"]
            one     = data["subtotal_one_time"]
            drivers = data["drivers"]

            # 카드
            _rect(ax, x0, rbot, col_w, ROW_H, C_WHITE, radius=0.006, edgecolor=C_BORDER, lw=0.8, zorder=2)
            cy = rtop - BP

            # 영역명 헤더
            NH = 0.052
            _rect(ax, x0+BP, cy-NH, col_w-BP*2, NH, C_NAVY, radius=0.004, edgecolor="none", zorder=3)
            ax.text(x0+col_w/2, cy-NH/2, area,
                    color=C_WHITE, fontsize=13, fontweight="bold",
                    va="center", ha="center", zorder=4)
            cy -= NH + BP*0.4

            # 금액 박스
            MH   = 0.068
            hw   = (col_w - BP*3) / 2

            _rect(ax, x0+BP, cy-MH, hw, MH, C_REC, radius=0.004, edgecolor=C_BORDER, lw=0.5, zorder=3)
            ax.text(x0+BP+hw/2, cy-MH*0.62, _fmt_m(rec, currency_symbol),
                    color=C_BLACK, fontsize=12, fontweight="bold", va="center", ha="center", zorder=4)
            ax.text(x0+BP+hw/2, cy-MH*0.18, "Recurring",
                    color=C_GRAY, fontsize=8, va="center", ha="center", zorder=4)

            ox = x0+BP*2+hw
            _rect(ax, ox, cy-MH, hw, MH, C_ONE, radius=0.004, edgecolor=C_BORDER, lw=0.5, zorder=3)
            ax.text(ox+hw/2, cy-MH*0.62, _fmt_m(one, currency_symbol) if one > 0 else "—",
                    color=C_BLACK, fontsize=12, fontweight="bold", va="center", ha="center", zorder=4)
            ax.text(ox+hw/2, cy-MH*0.18, "One-time",
                    color=C_GRAY, fontsize=8, va="center", ha="center", zorder=4)

            cy -= MH + BP*0.3
            ax.plot([x0+BP, x1-BP], [cy, cy], color=C_BORDER, lw=0.7, zorder=3)
            cy -= BP*0.3

            # 드라이버 목록
            avail = cy - rbot - BP
            n_drv = len(drivers)
            drh   = avail / max(n_drv, 1)

            for d in drivers:
                if cy - drh < rbot + BP*0.3:
                    break
                fill   = C_ONE if d["one_time"] else C_REC
                CW     = col_w * 0.33
                cx     = x1 - BP - CW
                cy_box = cy - drh*0.88
                _rect(ax, cx, cy_box, CW, drh*0.76, fill,
                      radius=0.003, edgecolor=C_BORDER, lw=0.4, zorder=3)
                ax.text(cx+CW/2, cy_box+drh*0.38, _fmt_m(d["benefit"], currency_symbol),
                        color=C_BLACK, fontsize=10, fontweight="bold",
                        va="center", ha="center", zorder=4)
                import textwrap
                char_limit = max(10, int((cx - x0 - BP*2) * FIG_W * 8.5))
                name_wrapped = "\n".join(textwrap.wrap(d["name"], width=char_limit)[:2])
                ax.text(x0+BP*1.5, cy-drh*0.5, name_wrapped,
                        color="#222222", fontsize=10,
                        va="center", ha="left", zorder=4, clip_on=True,
                        linespacing=1.2)
                cy -= drh

    ax.text(0.5, 0.001, "*Illustrative estimates based on industry benchmarks.",
            color=C_GRAY, fontsize=6.5, va="bottom", ha="center", style="italic")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight",
                facecolor=C_LGRAY, pad_inches=0.02)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def generate_project_economics_png(
    results: dict,
    currency_symbol: str,
    currency_code: str,
    realization_recurring: list[float],
    realization_onetime: list[float],
    discount_rate_pct: float,
) -> bytes:
    import numpy as np

    acv_by_year     = results["acv_by_year"]
    impl_cost       = results["impl_cost"]
    rec_annual      = results["annual_recurring_benefit"]
    one_total       = results["one_time_benefit"]
    real_rec        = [r / 100.0 for r in realization_recurring]
    real_one        = [r / 100.0 for r in realization_onetime]
    rec_by_year     = [rec_annual * real_rec[i] for i in range(5)]
    one_by_year     = [one_total  * real_one[i] for i in range(5)]
    cost_sub        = [-v / 1e6 for v in acv_by_year]
    cost_impl       = [-impl_cost / 1e6, 0, 0, 0, 0]
    benefit_by_year = results["benefit_by_year"]
    cost_by_year    = [acv_by_year[i] + (impl_cost if i == 0 else 0) for i in range(5)]

    cumulative = []
    cum = 0.0
    for i in range(5):
        cum += benefit_by_year[i] - cost_by_year[i]
        cumulative.append(cum / 1e6)

    npv         = results["npv"]
    npv_roi_pct = results["npv_roi_pct"]
    payback     = results["payback_years"]

    years = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    x     = np.arange(5)
    bar_w = 0.55

    # ── Canvas ──────────────────────────────────────────────────────────────────
    FIG_W, FIG_H = 13.0, 7.5
    fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor=C_LGRAY)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Header
    ax_hdr = fig.add_axes([0, 0.915, 1, 0.085])
    ax_hdr.set_xlim(0, 1); ax_hdr.set_ylim(0, 1); ax_hdr.axis("off")
    ax_hdr.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0",
                                    facecolor=C_NAVY, edgecolor="none", zorder=3))
    ax_hdr.text(0.012, 0.5, "Project Economics",
                color=C_WHITE, fontsize=24, fontweight="bold", va="center", zorder=4)
    ax_hdr.text(0.988, 0.5, f"Currency: {currency_code}",
                color="#A8C4E8", fontsize=12, va="center", ha="right", zorder=4)

    # ── 왼쪽: 차트 ──────────────────────────────────────────────────────────────
    ax = fig.add_axes([0.03, 0.10, 0.60, 0.78])
    ax.set_facecolor(C_WHITE)
    for spine in ax.spines.values():
        spine.set_color(C_BORDER)

    # 막대: subscription cost (네이비), impl cost (연보라), recurring benefit (하늘), one-time (연보라)
    bars_sub  = ax.bar(x, cost_sub,  bar_w, label="SAP Subscription Cost",          color=C_NAVY,        zorder=3)
    bars_impl = ax.bar(x, cost_impl, bar_w, bottom=cost_sub, label="Implementation Cost", color="#7B5EA7", zorder=3)
    bars_rec  = ax.bar(x, [v/1e6 for v in rec_by_year], bar_w, label="Recurring Benefits",  color=C_REC, edgecolor=C_BORDER, lw=0.5, zorder=3)
    bars_one  = ax.bar(x, [v/1e6 for v in one_by_year], bar_w,
                       bottom=[v/1e6 for v in rec_by_year],
                       label="One-time Benefits", color=C_ONE, edgecolor=C_BORDER, lw=0.5, zorder=3)

    # 누적 순이익 꺾은선
    ax.plot(x, cumulative, color=C_BLUE, lw=2.0, marker="o", markersize=5,
            label="Cumulative Net Benefit", zorder=4)

    # breakeven 참조선
    ax.axhline(0, color=C_BORDER, lw=0.8, zorder=2)

    # payback 수직선
    if 0 < payback < 5:
        ax.axvline(payback - 1, color="#5D36FF", lw=1.2, linestyle="--", zorder=3)
        ax.text(payback - 1 + 0.05, ax.get_ylim()[0] * 0.05 if ax.get_ylim()[0] < 0 else 0.2,
                f"Breakeven\n{payback:.1f} yrs",
                color="#5D36FF", fontsize=7.5, va="bottom", zorder=5)

    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=9)
    ax.tick_params(axis="y", labelsize=8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{currency_symbol}{v:.1f}M"))
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=C_BORDER, lw=0.5)

    ax.legend(fontsize=7, loc="upper left", framealpha=0.9,
              edgecolor=C_BORDER, facecolor=C_WHITE)

    # ── 오른쪽: KPI + Assumptions ────────────────────────────────────────────────
    ax_r = fig.add_axes([0.65, 0.10, 0.33, 0.78])
    ax_r.set_xlim(0, 1); ax_r.set_ylim(0, 1); ax_r.axis("off")

    def _kpi_box(ay, ah, val_text, label_text):
        _rect(ax_r, 0.02, ay, 0.96, ah, C_WHITE, radius=0.05, edgecolor=C_BORDER, lw=0.8, zorder=2)
        ax_r.text(0.5, ay + ah * 0.60, val_text,
                  color=C_BLUE, fontsize=20, fontweight="bold",
                  va="center", ha="center", zorder=3)
        ax_r.text(0.5, ay + ah * 0.22, label_text,
                  color=C_BLACK, fontsize=10, fontweight="bold",
                  va="center", ha="center", zorder=3)

    # KPI 3개: 위 70% 영역을 3등분
    kpi_top  = 1.00
    kpi_h    = 0.21
    kpi_gap  = 0.025
    for i, (val, lbl) in enumerate([
        (_fmt_m(npv, currency_symbol), "5-year NPV"),
        (f"{npv_roi_pct:.0f}%",        "5-year ROI"),
        (f"{payback:.1f} Yrs",          "Payback Period"),
    ]):
        ay = kpi_top - (i + 1) * kpi_h - i * kpi_gap
        _kpi_box(ay, kpi_h, val, lbl)

    # Assumptions 박스: 아래 28% 영역
    assump_top = kpi_top - 3 * kpi_h - 2 * kpi_gap - 0.03
    assump_h   = assump_top - 0.01
    _rect(ax_r, 0.02, 0.01, 0.96, assump_h, "#EEF2FA", radius=0.04, edgecolor=C_BORDER, lw=0.6, zorder=2)

    rec_str = " / ".join(f"Y{i+1}:{r:.0f}%" for i, r in enumerate(realization_recurring))
    one_str = " / ".join(f"Y{i+1}:{r:.0f}%" for i, r in enumerate(realization_onetime))
    assump_lines = [
        (f"Discount rate: {discount_rate_pct:.0f}%",  8.8, True),
        (f"Recurring: {rec_str}",                      8.0, False),
        (f"One-time:  {one_str}",                      8.0, False),
        ("*Illustrative estimates only.",               7.2, False),
    ]
    line_y = 0.01 + assump_h - 0.04
    for text, fs, bold in assump_lines:
        ax_r.text(0.07, line_y, text,
                  color=C_NAVY if bold else C_BLACK,
                  fontsize=fs, fontweight="bold" if bold else "normal",
                  va="top", ha="left", zorder=3)
        line_y -= 0.09

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight",
                facecolor=C_LGRAY, pad_inches=0.02)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
