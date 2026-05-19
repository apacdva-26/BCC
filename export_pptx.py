"""
PPTX export module for SAP Cloud ERP Business Case Calculator.
Slide 1: Value Tree  — template LOB blocks cloned & repositioned
Slide 2: Project Economics — template values filled in
"""
from __future__ import annotations
import copy, io
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree

TEMPLATE_PATH = "/Users/I589386/Library/CloudStorage/OneDrive-SAPSE(2)/DVA/BC Calculator/Presentation1.pptx"

C_BLUE    = RGBColor(0x00, 0x70, 0xF2)
C_BLACK   = RGBColor(0x00, 0x00, 0x00)
C_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
C_REC     = RGBColor(0xD1, 0xEF, 0xFF)   # recurring  – light blue
C_ONE     = RGBColor(0xE2, 0xD8, 0xFF)   # one-time   – light purple

EMU = 914400


# ─── helpers ──────────────────────────────────────────────────────────────────

def _rgb_hex(c: RGBColor) -> str:
    return f"{c[0]:02X}{c[1]:02X}{c[2]:02X}"


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


def _set_shape_pos(shape, left_in: float, top_in: float,
                   w_in: float | None = None, h_in: float | None = None):
    sp = shape._element
    xfrm = sp.find('.//' + qn('p:xfrm'))
    if xfrm is None:
        xfrm = sp.find('.//' + qn('a:xfrm'))
    if xfrm is None:
        return
    off = xfrm.find(qn('a:off'))
    ext = xfrm.find(qn('a:ext'))
    if off is not None:
        off.set('x', str(int(left_in * EMU)))
        off.set('y', str(int(top_in  * EMU)))
    if ext is not None:
        if w_in is not None:
            ext.set('cx', str(int(w_in * EMU)))
        if h_in is not None:
            ext.set('cy', str(int(h_in * EMU)))


def _set_run_text(shape, text: str, para_idx: int = 0, run_idx: int = 0):
    """Set text of a specific run in a shape's text frame."""
    try:
        para = shape.text_frame.paragraphs[para_idx]
        if run_idx < len(para.runs):
            para.runs[run_idx].text = text
        else:
            run = para.add_run()
            run.text = text
    except Exception:
        pass


def _clear_and_set_text(shape, lines: list[tuple[str, int, bool, RGBColor]],
                        align=PP_ALIGN.LEFT):
    """Replace all text in shape. lines = [(text, pt_size, bold, color), ...]"""
    tf = shape.text_frame
    tf.clear()
    for i, (text, pt, bold, color) in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        run = para.add_run()
        run.text = text
        run.font.size = Pt(pt)
        run.font.bold = bold
        run.font.color.rgb = color


def _clone_shape(slide, shape):
    """Deep-copy shape XML and add to slide's spTree."""
    sp_tree = slide.shapes._spTree
    new_el = copy.deepcopy(shape._element)
    sp_tree.append(new_el)
    # Return the new shape (last added)
    return slide.shapes[-1]


def _set_table_row_text(tbl_shape, row: int, col0: str, col1: str, col2: str,
                         col2_fill: RGBColor):
    """Set text in table row and optionally fill col2."""
    table = tbl_shape.table
    if row >= len(table.rows):
        return

    def _set(cell, txt, bold=False, align=PP_ALIGN.LEFT, fill_color=None):
        cell.text_frame.clear()
        para = cell.text_frame.paragraphs[0]
        para.alignment = align
        if txt:
            run = para.add_run()
            run.text = txt
            run.font.size = Pt(8)
            run.font.bold = bold
            run.font.color.rgb = C_BLACK
        if fill_color:
            tc = cell._tc
            tcPr = tc.find(qn('a:tcPr'))
            if tcPr is None:
                tcPr = etree.SubElement(tc, qn('a:tcPr'))
            # remove existing fill
            for existing in tcPr.findall(qn('a:solidFill')):
                tcPr.remove(existing)
            sf = etree.SubElement(tcPr, qn('a:solidFill'))
            clr = etree.SubElement(sf, qn('a:srgbClr'))
            clr.set('val', _rgb_hex(fill_color))

    _set(table.cell(row, 0), col0)
    _set(table.cell(row, 1), col1, align=PP_ALIGN.CENTER)
    _set(table.cell(row, 2), col2, bold=True, align=PP_ALIGN.CENTER, fill_color=col2_fill)


def _resize_table(tbl_shape, n_rows: int, row_h_in: float = 0.28):
    """Adjust table height and add/remove rows to match n_rows."""
    table = tbl_shape.table
    tbl_el = table._tbl

    # Target row height in EMU
    target_h = int(row_h_in * EMU)

    existing = list(tbl_el.findall(qn('a:tr')))
    current_n = len(existing)

    if n_rows > current_n:
        # Clone last row for each missing row
        ref_row = existing[-1]
        for _ in range(n_rows - current_n):
            new_row = copy.deepcopy(ref_row)
            tbl_el.append(new_row)
    elif n_rows < current_n:
        for row_el in existing[n_rows:]:
            tbl_el.remove(row_el)

    # Update row heights and total table height
    for tr in tbl_el.findall(qn('a:tr')):
        tr.set('h', str(target_h))

    total_h = target_h * n_rows
    xfrm = tbl_shape._element.find('.//' + qn('p:xfrm'))
    if xfrm is None:
        xfrm = tbl_shape._element.find('.//' + qn('a:xfrm'))
    if xfrm is not None:
        ext = xfrm.find(qn('a:ext'))
        if ext is not None:
            ext.set('cy', str(total_h))
    return total_h / EMU


# ─── Slide 1: Value Tree ──────────────────────────────────────────────────────

def _build_slide1(prs: Presentation, results: dict,
                  customer_name: str, currency_symbol: str, currency_code: str,
                  industry: str, maturity_label: str):

    slide = prs.slides[0]
    sp_tree = slide.shapes._spTree

    # Collect template block shapes (first block = Finance, index 0)
    lob_names_tmpl = [s for s in slide.shapes if s.name == 'Lob_Name_1']
    ob1s_tmpl      = [s for s in slide.shapes if s.name == 'ob1']
    rb1s_tmpl      = [s for s in slide.shapes if s.name == 'rb1']
    tables_tmpl    = [s for s in slide.shapes if s.name == 'tbl_lob2']
    lob4_tmpl      = next(s for s in slide.shapes if s.name == 'Lob_Name_4')
    r99_tmpl       = next(s for s in slide.shapes if s.name == 'Rectangle: Rounded Corners 99')
    r100_tmpl      = next(s for s in slide.shapes if s.name == 'Rectangle: Rounded Corners 100')

    # Reference block dimensions (from template block 0)
    ref = lob_names_tmpl[0]
    REF_LEFT = ref.left / EMU
    REF_TOP  = ref.top  / EMU
    # Relative offsets
    OB1_DL  = (ob1s_tmpl[0].left   - ref.left)   / EMU   # -0.413
    OB1_DT  = (ob1s_tmpl[0].top    - ref.top)    / EMU   # +0.384
    OB1_W   = ob1s_tmpl[0].width   / EMU
    OB1_H   = ob1s_tmpl[0].height  / EMU
    RB1_DL  = (rb1s_tmpl[0].left   - ref.left)   / EMU   # +0.702
    RB1_DT  = OB1_DT
    TBL_DL  = (tables_tmpl[0].left  - ref.left)  / EMU   # -0.511
    TBL_DT  = (tables_tmpl[0].top   - ref.top)   / EMU   # +0.817
    TBL_W   = tables_tmpl[0].width  / EMU
    LOB_W   = ref.width  / EMU
    LOB_H   = ref.height / EMU

    # Remove all existing LOB blocks from slide
    KEEP = {'Round Same Side Corner Rectangle 48',
            'Rectangle: Top Corners Rounded 60',
            'Rectangle: Top Corners Rounded 61',
            'Rectangle 62', 'Group 63', 'Title 1',
            'Left Bracket 98',
            'Lob_Name_4',
            'Rectangle: Rounded Corners 99',
            'Rectangle: Rounded Corners 100'}
    to_remove = [s for s in slide.shapes if s.name not in KEEP]
    for shape in to_remove:
        sp_tree.remove(shape._element)

    # Update title
    title = next(s for s in slide.shapes if s.name == 'Title 1')
    _clear_and_set_text(title, [("Value Tree", 14, True, C_BLACK)])

    # Update info box
    info_box = next(s for s in slide.shapes if s.name == 'Rectangle 62')
    _clear_and_set_text(info_box, [
        (f"Currency: {currency_code}", 7, True, C_WHITE),
        (f"Industry: {industry}", 7, False, C_WHITE),
        (f"Maturity: {maturity_label}", 7, False, C_WHITE),
        ("*Illustrative estimates based on industry benchmarks.", 6, False, C_WHITE),
    ])

    # Layout: 7 areas in 2 rows (4 + 3), fitting within slide width
    AREAS = [
        ["Asset Management", "Finance", "Manufacturing", "Sales"],
        ["Procurement", "R&D", "Supply Chain"],
    ]

    # Usable area
    SLIDE_W     = 10.90    # inches, leaving room for info box on right
    START_LEFT  = 0.15
    ROW_TOPS    = [1.05, 4.10]
    BLOCK_H     = 2.80     # total block height including table
    ROW_H_IN    = 0.28     # each table row height

    def _place_block(area: str, left_in: float, top_in: float, col_w: float):
        data = results["by_area"].get(area)
        if not data:
            return

        rec      = data["subtotal_recurring"]
        one      = data["subtotal_one_time"]
        drivers  = data["drivers"]
        n_rows   = len(drivers)

        # --- Clone Lob_Name_1 ---
        lob_clone = _clone_shape(slide, lob_names_tmpl[0])
        _set_shape_pos(lob_clone, left_in + (col_w - LOB_W) / 2, top_in,
                       col_w * 0.80, LOB_H)
        _clear_and_set_text(lob_clone, [(area, 8, True, C_BLACK)])

        # metric boxes width: split evenly within col
        metric_w = col_w / 2 - 0.04
        metric_top = top_in + LOB_H + 0.05

        # --- Clone ob1 (Recurring) ---
        ob1_clone = _clone_shape(slide, ob1s_tmpl[0])
        _set_shape_pos(ob1_clone, left_in, metric_top, metric_w, OB1_H)
        _clear_and_set_text(ob1_clone, [(_fmt_m(rec, currency_symbol), 9, True, C_BLACK)],
                            align=PP_ALIGN.CENTER)

        # --- Clone rb1 (One-time) ---
        rb1_clone = _clone_shape(slide, rb1s_tmpl[0])
        _set_shape_pos(rb1_clone, left_in + metric_w + 0.08, metric_top, metric_w, OB1_H)
        _clear_and_set_text(rb1_clone,
                            [(_fmt_m(one, currency_symbol) if one > 0 else "-", 9, True, C_BLACK)],
                            align=PP_ALIGN.CENTER)

        # --- Clone tbl_lob2 ---
        tbl_clone = _clone_shape(slide, tables_tmpl[0])
        tbl_top   = metric_top + OB1_H + 0.05
        tbl_h_avail = BLOCK_H - (tbl_top - top_in) - 0.05
        _set_shape_pos(tbl_clone, left_in, tbl_top, col_w, None)

        # Adjust row count & height
        _resize_table(tbl_clone, n_rows, min(ROW_H_IN, tbl_h_avail / max(n_rows, 1)))

        # Fill table rows
        for r, d in enumerate(drivers):
            fill = C_ONE if d["one_time"] else C_REC
            _set_table_row_text(
                tbl_clone, r,
                d["name"],
                f"{d['improvement_pct']:.0f}%",
                _fmt_m(d["benefit"], currency_symbol),
                fill
            )

    # Draw rows
    for row_idx, row_areas in enumerate(AREAS):
        n = len(row_areas)
        col_w = SLIDE_W / n
        for col_idx, area in enumerate(row_areas):
            left = START_LEFT + col_idx * col_w
            _place_block(area, left, ROW_TOPS[row_idx], col_w)

    # User Productivity in total
    prod         = results["productivity"]
    total_rec    = results["annual_recurring_benefit"]
    total_one    = results["one_time_benefit"]

    # Update Lob_Name_4 (total label)
    lob4 = next(s for s in slide.shapes if s.name == 'Lob_Name_4')
    _clear_and_set_text(lob4, [
        (f"Total Steady-state Value Potential for {customer_name}", 10, True, C_BLACK),
    ])
    _set_shape_pos(lob4, START_LEFT, 0.62, SLIDE_W, 0.32)

    # Update r99 (recurring total)
    r99 = next(s for s in slide.shapes if s.name == 'Rectangle: Rounded Corners 99')
    _set_shape_pos(r99, START_LEFT + SLIDE_W * 0.55, 0.62, 2.0, 0.32)
    _clear_and_set_text(r99,
        [(f"Recurring: {_fmt_m(total_rec, currency_symbol)}", 10, True, C_BLACK)],
        align=PP_ALIGN.CENTER)

    # Update r100 (one-time total)
    r100 = next(s for s in slide.shapes if s.name == 'Rectangle: Rounded Corners 100')
    _set_shape_pos(r100, START_LEFT + SLIDE_W * 0.55 + 2.1, 0.62, 2.0, 0.32)
    _clear_and_set_text(r100,
        [(f"One-time: {_fmt_m(total_one, currency_symbol)}", 10, True, C_BLACK)],
        align=PP_ALIGN.CENTER)


# ─── Slide 2: Project Economics ───────────────────────────────────────────────

def _build_slide2(prs: Presentation, results: dict,
                  currency_symbol: str, currency_code: str,
                  realization_recurring: list[float],
                  realization_onetime: list[float],
                  discount_rate_pct: float):

    from pptx.chart.data import ChartData

    slide = prs.slides[1]

    acv_by_year = results["acv_by_year"]
    impl_cost   = results["impl_cost"]
    rec_annual  = results["annual_recurring_benefit"]
    one_total   = results["one_time_benefit"]
    real_rec    = [r / 100.0 for r in realization_recurring]
    real_one    = [r / 100.0 for r in realization_onetime]

    rec_by_year  = [rec_annual * real_rec[i] for i in range(5)]
    one_by_year  = [one_total  * real_one[i] for i in range(5)]
    cost_by_year = [acv_by_year[i] + (impl_cost if i == 0 else 0) for i in range(5)]
    benefit_by_year = results["benefit_by_year"]

    cumulative = []
    cum = 0.0
    for i in range(5):
        cum += benefit_by_year[i] - cost_by_year[i]
        cumulative.append(cum)

    # Chart
    chart_shape = next(s for s in slide.shapes if s.name == 'Chart 17')
    chart = chart_shape.chart
    cd = ChartData()
    cd.categories = ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5']
    cd.add_series('SAP Subscription Cost',           [-v / 1e6 for v in acv_by_year])
    cd.add_series('Partner Implementation Cost',     [-impl_cost / 1e6, 0, 0, 0, 0])
    cd.add_series('Recurring Annual Benefits',        [v / 1e6 for v in rec_by_year])
    cd.add_series('One-time Free Cashflow Benefits',  [v / 1e6 for v in one_by_year])
    cd.add_series('Cumulative Benefits',              [v / 1e6 for v in cumulative])
    chart.replace_data(cd)

    # KPI boxes
    npv         = results["npv"]
    npv_roi_pct = results["npv_roi_pct"]
    payback     = results["payback_years"]

    def _set_kpi(shape_name, val_text, label_text):
        shape = next(s for s in slide.shapes if s.name == shape_name)
        tf = shape.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        r1 = p1.add_run()
        r1.text = val_text
        r1.font.size = Pt(16)
        r1.font.bold = True
        r1.font.color.rgb = C_BLUE
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run()
        r2.text = label_text
        r2.font.size = Pt(11)
        r2.font.bold = True
        r2.font.color.rgb = C_BLACK

    _set_kpi('Rectangle: Rounded Corners 20', _fmt_m(npv, currency_symbol), '5-year NPV')
    _set_kpi('Rectangle: Rounded Corners 21', f"{npv_roi_pct:.0f}%",         '5-year ROI')
    _set_kpi('Rectangle: Rounded Corners 22', f"{payback:.1f} Yrs",          'Payback Period')

    # Breakeven label
    be = next(s for s in slide.shapes if s.name == 'TextBox 18')
    be.text_frame.paragraphs[0].runs[0].text = f"Breakeven at {payback:.1f} years"

    # Assumptions box
    assump = next(s for s in slide.shapes if s.name == 'Rectangle 23')
    rec_str = " / ".join(f"{r:.0f}%Y{i+1}" for i, r in enumerate(realization_recurring))
    one_str = " / ".join(f"{r:.0f}%Y{i+1}" for i, r in enumerate(realization_onetime))
    _clear_and_set_text(assump, [
        ("Assumptions for Benefits:", 7, True,  C_BLACK),
        ("Benefits estimated based on outside-in, conservative benchmarks.", 6.5, False, C_BLACK),
        ("Annual amounts shown in nominal value (no inflation adjustment).", 6.5, False, C_BLACK),
        (f"Recurring realization: {rec_str}", 6.5, False, C_BLACK),
        (f"One-time realization:  {one_str}",  6.5, False, C_BLACK),
        ("", 4, False, C_BLACK),
        ("Assumptions for Costs:", 7, True,  C_BLACK),
        ("All costs are illustrative only.", 6.5, False, C_BLACK),
        (f"Discount rate: {discount_rate_pct:.0f}% for NPV calculation.", 6.5, False, C_BLACK),
        ("Subscription costs as per TCO comparison.", 6.5, False, C_BLACK),
        ("*Illustrative estimates only. Further discovery required.", 6, False, C_BLACK),
    ])


# ─── Public API ───────────────────────────────────────────────────────────────

def generate_pptx(
    results: dict,
    customer_name: str,
    currency_symbol: str,
    currency_code: str,
    industry: str,
    maturity_label: str,
    realization_recurring: list[float],
    realization_onetime: list[float],
    discount_rate_pct: float,
) -> bytes:
    prs = Presentation(TEMPLATE_PATH)
    _build_slide1(prs, results, customer_name, currency_symbol, currency_code,
                  industry, maturity_label)
    _build_slide2(prs, results, currency_symbol, currency_code,
                  realization_recurring, realization_onetime, discount_rate_pct)
    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.read()
