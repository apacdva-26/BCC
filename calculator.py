from __future__ import annotations
import numpy_financial as npf
from industry_data import get_benchmark, get_cogs_pct, get_mfg_cost_pct, get_direct_spend_params

# Value Driver definitions
# baseline_type:
#   "revenue_pct"        → baseline = revenue × (benchmark / 100)
#   "cogs_pct"           → baseline = revenue × (cogs_pct/100) × (benchmark / 100)
#   "days_revenue"       → baseline = revenue / 365 × benchmark                        (DSO)
#   "days_cogs"          → baseline = revenue × (cogs_pct/100) / 365 × benchmark       (DPO, DII)
#   "direct_spend_pct"   → baseline = revenue × (mfg_cost_pct/100) × (direct_material_pct/100) × (benchmark/100)

VALUE_DRIVERS: list[dict] = [
    # Asset Management
    {
        "area": "Asset Management",
        "name": "Reduce Asset Maintenance Cost",
        "baseline_type": "revenue_pct",
        "benchmark_kpi": "asset_maintenance_cost_pct_revenue",
        "improvement_pct": 10.0,
        "one_time": False,
    },
    {
        "area": "Asset Management",
        "name": "Reduce Unplanned Downtime",
        "baseline_type": "revenue_pct",
        "benchmark_kpi": "unplanned_downtime_pct",
        "improvement_pct": 15.0,
        "one_time": False,
    },
    # Finance
    {
        "area": "Finance",
        "name": "Reduce Days Sales Outstanding",
        "baseline_type": "days_revenue",
        "benchmark_kpi": "days_sales_outstanding",
        "improvement_pct": 5.0,
        "one_time": True,
    },
    {
        "area": "Finance",
        "name": "Improve Days Payable Outstanding",
        "baseline_type": "days_cogs",
        "benchmark_kpi": "days_payable_outstanding",
        "improvement_pct": 5.0,
        "one_time": True,
    },
    {
        "area": "Finance",
        "name": "Reduce Finance Cost",
        "baseline_type": "revenue_pct",
        "benchmark_kpi": "finance_cost_pct_revenue",
        "improvement_pct": 10.0,
        "one_time": False,
    },
    # Manufacturing
    {
        "area": "Manufacturing",
        "name": "Reduce Total Manufacturing Cost",
        "baseline_type": "revenue_pct",
        "benchmark_kpi": "manufacturing_cost_pct_revenue",
        "improvement_pct": 5.0,
        "one_time": False,
    },
    # Sales
    {
        "area": "Sales",
        "name": "Reduce Sales Cost",
        "baseline_type": "revenue_pct",
        "benchmark_kpi": "sales_cost_pct_revenue",
        "improvement_pct": 10.0,
        "one_time": False,
    },
    # Procurement
    {
        "area": "Procurement",
        "name": "Improve Sourcing Savings on Direct Spend",
        "baseline_type": "direct_spend_pct",
        "benchmark_kpi": "direct_material_cost_pct_mfg",
        "improvement_pct": 5.0,
        "one_time": False,
    },
    {
        "area": "Procurement",
        "name": "Reduce Invoice Error Rate",
        "baseline_type": "revenue_pct",
        "benchmark_kpi": "invoice_error_rate_pct",
        "improvement_pct": 20.0,
        "one_time": False,
    },
    # R&D
    {
        "area": "R&D",
        "name": "Optimize R&D Expense",
        "baseline_type": "revenue_pct",
        "benchmark_kpi": "rd_expense_pct_revenue",
        "improvement_pct": 10.0,
        "one_time": False,
    },
    # Supply Chain
    {
        "area": "Supply Chain",
        "name": "Reduce Total Logistics Cost",
        "baseline_type": "cogs_pct",
        "benchmark_kpi": "total_logistics_cost_pct_cogs",
        "improvement_pct": 10.0,
        "one_time": False,
    },
    {
        "area": "Supply Chain",
        "name": "Reduce Days in Inventory",
        "baseline_type": "days_cogs",
        "benchmark_kpi": "days_in_inventory",
        "improvement_pct": 5.0,
        "one_time": True,
    },
    {
        "area": "Supply Chain",
        "name": "Reduce Inventory Carrying Cost",
        "baseline_type": "revenue_pct",
        "benchmark_kpi": "inventory_carrying_cost_pct_revenue",
        "improvement_pct": 15.0,
        "one_time": False,
    },
]


def _get_baseline(vd: dict, revenue: float, industry: str, maturity: str) -> float | None:
    benchmark = get_benchmark(vd["benchmark_kpi"], industry, maturity)
    if benchmark is None:
        return None

    btype = vd["baseline_type"]
    if btype == "revenue_pct":
        return revenue * (benchmark / 100.0)
    elif btype == "cogs_pct":
        cogs_pct = get_cogs_pct(industry, maturity)
        cogs = revenue * (cogs_pct / 100.0)
        return cogs * (benchmark / 100.0)
    elif btype == "days_revenue":
        return (revenue / 365.0) * benchmark
    elif btype == "days_cogs":
        cogs_pct = get_cogs_pct(industry, maturity)
        cogs = revenue * (cogs_pct / 100.0)
        return (cogs / 365.0) * benchmark
    elif btype == "direct_spend_pct":
        mfg_cost_pct = get_mfg_cost_pct(industry, maturity)
        if mfg_cost_pct is None:
            return None
        direct_material_pct = benchmark
        params = get_direct_spend_params(maturity)
        spend_under_mgmt = params["spend_under_mgmt_pct"] / 100.0
        sourcing_savings = params["sourcing_savings_rate_pct"] / 100.0
        return revenue * (mfg_cost_pct / 100.0) * (direct_material_pct / 100.0) * spend_under_mgmt * sourcing_savings
    return None


def calculate_benefits(
    revenue: float,
    acv_by_year: list[float],
    impl_cost: float,
    num_users: int,
    avg_salary: float,
    productivity_pct: float,
    selected_areas: list[str],
    industry: str,
    maturity: str,
    improvement_overrides: dict[str, float] | None = None,
    realization_recurring: list[float] | None = None,
    realization_onetime: list[float] | None = None,
    discount_rate_pct: float = 14.0,
    scalar: float = 1.0,
) -> dict:
    overrides = improvement_overrides or {}
    real_rec = [r / 100.0 for r in (realization_recurring or [100.0] * 5)]
    real_one = [r / 100.0 for r in (realization_onetime  or [100.0] * 5)]

    results_by_area: dict[str, dict] = {}
    total_recurring = 0.0
    total_one_time = 0.0

    for area in selected_areas:
        area_drivers = [vd for vd in VALUE_DRIVERS if vd["area"] == area]
        area_total_recurring = 0.0
        area_total_one_time = 0.0
        area_items = []

        for vd in area_drivers:
            baseline = _get_baseline(vd, revenue, industry, maturity)
            if baseline is None:
                continue
            imp_pct = overrides.get(vd["name"], vd["improvement_pct"]) * scalar
            benefit = baseline * (imp_pct / 100.0)
            is_one_time = vd.get("one_time", False)
            area_total_recurring += 0 if is_one_time else benefit
            area_total_one_time += benefit if is_one_time else 0
            item = {
                "name": vd["name"],
                "baseline": baseline,
                "improvement_pct": imp_pct,
                "benefit": benefit,
                "one_time": is_one_time,
                "benchmark_kpi": vd["benchmark_kpi"],
                "baseline_type": vd["baseline_type"],
            }
            if vd["baseline_type"] == "direct_spend_pct":
                from industry_data import get_direct_spend_params
                params = get_direct_spend_params(maturity)
                item["spend_under_mgmt_pct"] = params["spend_under_mgmt_pct"]
                item["sourcing_savings_rate_pct"] = params["sourcing_savings_rate_pct"]
            area_items.append(item)

        results_by_area[area] = {
            "drivers": area_items,
            "subtotal_recurring": area_total_recurring,
            "subtotal_one_time": area_total_one_time,
            "subtotal": area_total_recurring + area_total_one_time,
        }
        total_recurring += area_total_recurring
        total_one_time += area_total_one_time

    # User Productivity (recurring)
    productivity_baseline = num_users * avg_salary
    productivity_benefit = productivity_baseline * (productivity_pct / 100.0)
    total_recurring += productivity_benefit

    # Year-by-year benefit with realization rates
    benefit_by_year = [
        total_recurring * real_rec[i] + total_one_time * real_one[i]
        for i in range(5)
    ]

    five_year_benefit = sum(benefit_by_year)
    subscription_cost = sum(acv_by_year)
    total_cost = subscription_cost + impl_cost
    net_benefit = five_year_benefit - total_cost
    roi_pct = (net_benefit / total_cost * 100) if total_cost > 0 else 0

    # NPV: discount each year's net cash flow (benefit - cost)
    r = discount_rate_pct / 100.0
    cost_by_year = [acv_by_year[i] + (impl_cost if i == 0 else 0) for i in range(5)]
    npv = sum(
        (benefit_by_year[i] - cost_by_year[i]) / ((1 + r) ** (i + 1))
        for i in range(5)
    )
    npv_roi_pct = (npv / total_cost * 100) if total_cost > 0 else 0

    # IRR: Year 0 = -impl_cost, Years 1-5 = benefit - ACV
    irr_cashflows = [-impl_cost] + [benefit_by_year[i] - acv_by_year[i] for i in range(5)]
    try:
        irr_val = npf.irr(irr_cashflows)
        irr_pct = irr_val * 100 if irr_val is not None and not (irr_val != irr_val) else None
    except Exception:
        irr_pct = None

    # Payback: cumulative benefit vs total cost
    payback_years = 0.0
    cumulative = 0.0
    for i, yr_benefit in enumerate(benefit_by_year):
        if yr_benefit <= 0:
            continue
        prev_cumulative = cumulative
        cumulative += yr_benefit
        if cumulative >= total_cost:
            fraction = (total_cost - prev_cumulative) / yr_benefit
            payback_years = i + fraction
            break
    else:
        payback_years = total_cost / (five_year_benefit / 5) if five_year_benefit > 0 else 0

    return {
        "by_area": results_by_area,
        "productivity": {
            "num_users": num_users,
            "avg_salary": avg_salary,
            "benefit_pct": productivity_pct,
            "baseline": productivity_baseline,
            "annual_benefit": productivity_benefit,
        },
        "annual_recurring_benefit": total_recurring,
        "one_time_benefit": total_one_time,
        "benefit_by_year": benefit_by_year,
        "five_year_benefit": five_year_benefit,
        "five_year_subscription": subscription_cost,
        "acv_by_year": acv_by_year,
        "impl_cost": impl_cost,
        "five_year_cost": total_cost,
        "net_benefit": net_benefit,
        "roi_pct": roi_pct,
        "npv": npv,
        "npv_roi_pct": npv_roi_pct,
        "irr_pct": irr_pct,
        "discount_rate_pct": discount_rate_pct,
        "payback_years": payback_years,
        "scalar": scalar,
    }


def find_scalar(
    revenue: float,
    acv_by_year: list[float],
    impl_cost: float,
    num_users: int,
    avg_salary: float,
    productivity_pct: float,
    selected_areas: list[str],
    industry: str,
    maturity: str,
    improvement_overrides: dict[str, float] | None = None,
    realization_recurring: list[float] | None = None,
    realization_onetime: list[float] | None = None,
    discount_rate_pct: float = 14.0,
    irr_target: tuple[float, float] = (15.0, 60.0),
    payback_target: tuple[float, float] = (1.0, 2.5),
    scalar_step: float = 0.05,
) -> float:
    """Return the largest discrete scalar (stepped by scalar_step) that satisfies
    both IRR and Payback targets. Falls back to 1.0 if no candidate satisfies both."""

    def _run(s: float) -> dict:
        return calculate_benefits(
            revenue, acv_by_year, impl_cost, num_users, avg_salary,
            productivity_pct, selected_areas, industry, maturity,
            improvement_overrides=improvement_overrides,
            realization_recurring=realization_recurring,
            realization_onetime=realization_onetime,
            discount_rate_pct=discount_rate_pct,
            scalar=s,
        )

    irr_lo, irr_hi = irr_target
    pb_lo, pb_hi = payback_target

    # Build discrete candidates from largest to smallest
    n_steps = max(1, round(1.0 / scalar_step))
    candidates = [round(i / n_steps, 10) for i in range(n_steps, 0, -1)]

    for s in candidates:
        r  = _run(s)
        pb = r["payback_years"]
        if pb_lo <= pb <= pb_hi:
            return s

    return candidates[-1]
