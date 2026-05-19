"""
Industry benchmark data extracted from SAP BC Calculator Excel files.

Structure per KPI:
  { "top": float, "average": float, "bottom": float }

baseline_type:
  "revenue_pct"  → baseline = revenue × (peer_value / 100)
  "cogs_pct"     → baseline = revenue × (cogs_pct/100) × (peer_value/100)
  "days"         → baseline = revenue / 365 × peer_value   (for DSO/DPO/DII)

improvement_pct: the benefit % applied on top of baseline (from pptx, editable in admin)
"""

from __future__ import annotations

# ── Improvement % defaults (from BusinessCase pptx, High Tech) ────────────────
# These are stored in vd_config and editable via Admin page.
# Kept here as reference only.

# ── COGS % of revenue per industry (Top/Average/Bottom) ──────────────────────
COGS_PCT: dict[str, dict] = {
    "Agriculture":                          {"top": 53.6, "average": 69.2, "bottom": 88.0},
    "Automotive":                           {"top": 74.0, "average": 81.2, "bottom": 86.5},
    "Chemical":                             {"top": 59.6, "average": 69.7, "bottom": 77.4},
    "Consumer Products":                    {"top": 48.0, "average": 60.6, "bottom": 75.0},
    "Engineering, Construction & Operations": {"top": 60.0, "average": 71.7, "bottom": 79.2},
    "High Tech":                            {"top": 44.4, "average": 55.3, "bottom": 68.0},
    "Industrial Manufacturing":             {"top": 61.2, "average": 69.8, "bottom": 78.8},
    "Life Sciences":                        {"top": 25.5, "average": 36.4, "bottom": 47.7},
    "Mill Products":                        {"top": 57.0, "average": 70.1, "bottom": 80.8},
    "Oil, Gas & Energy":                    {"top": 52.1, "average": 65.7, "bottom": 85.2},
    "Professional Services":                {"top": 42.9, "average": 56.4, "bottom": 69.5},
    "Retail":                               {"top": 50.0, "average": 61.5, "bottom": 76.2},
    "Telecommunications":                   {"top": 38.9, "average": 54.8, "bottom": 69.3},
    "Travel & Transportation":              {"top": 42.1, "average": 57.1, "bottom": 77.7},
    "Utilities":                            {"top": 28.3, "average": 47.7, "bottom": 69.7},
    "Wholesale Distribution":               {"top": 68.0, "average": 78.6, "bottom": 86.4},
}

# ── KPI benchmarks per industry ───────────────────────────────────────────────
# Key = KPI identifier (matches VALUE_DRIVERS baseline_kpi field)
# Value = dict of industry → {top, average, bottom}

BENCHMARKS: dict[str, dict[str, dict]] = {

    "asset_maintenance_cost_pct_revenue": {
        "Agriculture":                          {"top": 1.4,  "average": 2.4,  "bottom": 3.5},
        "Automotive":                           {"top": 0.8,  "average": 2.0,  "bottom": 3.3},
        "Chemical":                             {"top": 1.7,  "average": 3.0,  "bottom": 4.6},
        "Consumer Products":                    {"top": 1.3,  "average": 2.5,  "bottom": 3.8},
        "Engineering, Construction & Operations": {"top": 1.5, "average": 3.9, "bottom": 7.0},
        "High Tech":                            {"top": 1.2,  "average": 2.1,  "bottom": 3.3},
        "Industrial Manufacturing":             {"top": 0.8,  "average": 3.6,  "bottom": 5.4},
        "Life Sciences":                        {"top": 1.3,  "average": 3.9,  "bottom": 6.2},
        "Mill Products":                        {"top": 1.2,  "average": 3.6,  "bottom": 5.0},
        "Oil, Gas & Energy":                    {"top": 1.6,  "average": 4.2,  "bottom": 7.8},
        "Retail":                               {"top": 1.0,  "average": 1.6,  "bottom": 3.0},
        "Telecommunications":                   {"top": 1.0,  "average": 1.6,  "bottom": 3.0},  # proxy: Retail
        "Travel & Transportation":              {"top": 3.0,  "average": 6.4,  "bottom": 9.0},
        "Wholesale Distribution":               {"top": 0.8,  "average": 3.6,  "bottom": 5.4},  # proxy: Industrial Manufacturing
        "Utilities":                            {"top": 1.8,  "average": 5.3,  "bottom": 9.1},
    },

    "unplanned_downtime_pct": {
        "Agriculture":                          {"top": 5.0,  "average": 7.5,  "bottom": 10.0},
        "Automotive":                           {"top": 3.9,  "average": 4.7,  "bottom": 6.0},
        "Chemical":                             {"top": 3.0,  "average": 7.2,  "bottom": 10.0},
        "Consumer Products":                    {"top": 5.0,  "average": 8.4,  "bottom": 12.0},
        "Engineering, Construction & Operations": {"top": 5.0, "average": 7.6, "bottom": 10.0},  # proxy: Industrial Manufacturing
        "High Tech":                            {"top": 3.9,  "average": 4.7,  "bottom": 6.0},   # proxy: Automotive
        "Industrial Manufacturing":             {"top": 5.0,  "average": 7.6,  "bottom": 10.0},
        "Life Sciences":                        {"top": 3.0,  "average": 7.2,  "bottom": 10.0},  # proxy: Chemical
        "Mill Products":                        {"top": 6.0,  "average": 8.7,  "bottom": 15.0},
        "Oil, Gas & Energy":                    {"top": 2.0,  "average": 3.9,  "bottom": 7.0},
        "Telecommunications":                   {"top": 1.0,  "average": 6.1,  "bottom": 10.0},  # proxy: Utilities
        "Travel & Transportation":              {"top": 2.0,  "average": 3.5,  "bottom": 4.0},
        "Utilities":                            {"top": 1.0,  "average": 6.1,  "bottom": 10.0},
    },

    "days_sales_outstanding": {
        "Agriculture":                          {"top": 30.6, "average": 39.1, "bottom": 50.0},
        "Automotive":                           {"top": 30.0, "average": 46.6, "bottom": 60.0},
        "Chemical":                             {"top": 38.9, "average": 48.7, "bottom": 59.9},
        "Consumer Products":                    {"top": 29.0, "average": 40.9, "bottom": 55.0},
        "Engineering, Construction & Operations": {"top": 30.0, "average": 64.0, "bottom": 90.0},
        "High Tech":                            {"top": 42.0, "average": 50.8, "bottom": 60.0},
        "Industrial Manufacturing":             {"top": 40.0, "average": 54.9, "bottom": 70.0},
        "Life Sciences":                        {"top": 55.0, "average": 64.3, "bottom": 76.0},
        "Mill Products":                        {"top": 32.9, "average": 45.2, "bottom": 60.0},
        "Oil, Gas & Energy":                    {"top": 27.0, "average": 48.8, "bottom": 66.0},
        "Professional Services":                {"top": 32.0, "average": 47.6, "bottom": 60.0},
        "Retail":                               {"top": 7.4,  "average": 22.0, "bottom": 39.0},
        "Telecommunications":                   {"top": 36.5, "average": 50.0, "bottom": 56.6},
        "Travel & Transportation":              {"top": 30.0, "average": 43.6, "bottom": 65.0},
        "Utilities":                            {"top": 24.7, "average": 42.9, "bottom": 57.0},
        "Wholesale Distribution":               {"top": 32.0, "average": 43.1, "bottom": 60.0},
    },

    "days_payable_outstanding": {
        "Agriculture":                          {"top": 60.0, "average": 44.0, "bottom": 30.0},
        "Automotive":                           {"top": 74.0, "average": 55.0, "bottom": 35.0},
        "Chemical":                             {"top": 67.0, "average": 53.0, "bottom": 42.0},
        "Consumer Products":                    {"top": 62.0, "average": 46.0, "bottom": 30.0},
        "Engineering, Construction & Operations": {"top": 73.0, "average": 53.0, "bottom": 30.0},
        "High Tech":                            {"top": 70.0, "average": 53.0, "bottom": 35.0},
        "Industrial Manufacturing":             {"top": 65.0, "average": 51.0, "bottom": 30.0},
        "Life Sciences":                        {"top": 69.0, "average": 55.0, "bottom": 42.0},
        "Mill Products":                        {"top": 62.0, "average": 46.0, "bottom": 30.0},
        "Oil, Gas & Energy":                    {"top": 75.0, "average": 51.0, "bottom": 30.0},
        "Professional Services":                {"top": 51.0, "average": 37.0, "bottom": 30.0},
        "Retail":                               {"top": 58.0, "average": 44.0, "bottom": 30.0},
        "Telecommunications":                   {"top": 63.0, "average": 48.0, "bottom": 30.0},
        "Travel & Transportation":              {"top": 60.0, "average": 44.0, "bottom": 30.0},
        "Utilities":                            {"top": 61.0, "average": 42.0, "bottom": 27.0},
        "Wholesale Distribution":               {"top": 56.0, "average": 40.0, "bottom": 29.0},
    },

    "finance_cost_pct_revenue": {
        "Agriculture":                          {"top": 0.50, "average": 0.79, "bottom": 1.11},
        "Automotive":                           {"top": 0.47, "average": 0.79, "bottom": 1.06},
        "Chemical":                             {"top": 0.62, "average": 0.86, "bottom": 1.28},
        "Consumer Products":                    {"top": 0.67, "average": 1.06, "bottom": 1.63},
        "Engineering, Construction & Operations": {"top": 0.36, "average": 0.90, "bottom": 1.49},
        "High Tech":                            {"top": 0.63, "average": 1.38, "bottom": 2.09},
        "Industrial Manufacturing":             {"top": 0.59, "average": 1.01, "bottom": 1.62},
        "Life Sciences":                        {"top": 1.00, "average": 1.56, "bottom": 2.21},
        "Mill Products":                        {"top": 0.38, "average": 1.04, "bottom": 1.72},
        "Oil, Gas & Energy":                    {"top": 0.30, "average": 1.16, "bottom": 2.28},
        "Professional Services":                {"top": 0.93, "average": 1.33, "bottom": 1.91},
        "Retail":                               {"top": 0.53, "average": 0.89, "bottom": 1.53},
        "Telecommunications":                   {"top": 0.76, "average": 1.47, "bottom": 1.96},
        "Travel & Transportation":              {"top": 0.48, "average": 0.89, "bottom": 1.38},
        "Utilities":                            {"top": 0.56, "average": 0.74, "bottom": 1.01},
        "Wholesale Distribution":               {"top": 0.45, "average": 0.79, "bottom": 1.16},
    },

    "manufacturing_cost_pct_revenue": {
        "Agriculture":                          {"top": 43.7, "average": 56.1, "bottom": 61.6},
        "Automotive":                           {"top": 15.6, "average": 55.6, "bottom": 78.1},
        "Chemical":                             {"top": 36.1, "average": 48.3, "bottom": 57.0},
        "Consumer Products":                    {"top": 27.8, "average": 46.2, "bottom": 61.6},
        "High Tech":                            {"top": 27.7, "average": 44.7, "bottom": 84.0},
        "Industrial Manufacturing":             {"top": 28.2, "average": 57.9, "bottom": 82.4},
        "Life Sciences":                        {"top": 21.1, "average": 36.3, "bottom": 49.9},
        "Mill Products":                        {"top": 23.4, "average": 55.1, "bottom": 73.5},
    },

    "sales_cost_pct_revenue": {
        "Agriculture":                          {"top": 0.86, "average": 3.89, "bottom": 7.00},
        "Automotive":                           {"top": 1.08, "average": 5.24, "bottom": 8.16},
        "Chemical":                             {"top": 2.45, "average": 4.31, "bottom": 8.99},  # proxy: Industrial Manufacturing
        "Consumer Products":                    {"top": 1.04, "average": 6.10, "bottom": 10.32},
        "Engineering, Construction & Operations": {"top": 2.45, "average": 4.31, "bottom": 8.99},  # proxy: Industrial Manufacturing
        "High Tech":                            {"top": 3.00, "average": 6.91, "bottom": 10.00},
        "Industrial Manufacturing":             {"top": 2.45, "average": 4.31, "bottom": 8.99},
        "Life Sciences":                        {"top": 3.00, "average": 6.91, "bottom": 10.00},  # proxy: High Tech
        "Mill Products":                        {"top": 2.22, "average": 4.25, "bottom": 7.56},
        "Oil, Gas & Energy":                    {"top": 2.45, "average": 4.31, "bottom": 8.99},  # proxy: Industrial Manufacturing
        "Professional Services":                {"top": 1.67, "average": 4.09, "bottom": 5.98},
        "Retail":                               {"top": 1.04, "average": 6.10, "bottom": 10.32},  # proxy: Consumer Products
        "Telecommunications":                   {"top": 3.00, "average": 6.91, "bottom": 10.00},  # proxy: High Tech
        "Travel & Transportation":              {"top": 1.67, "average": 4.09, "bottom": 5.98},  # proxy: Professional Services
        "Utilities":                            {"top": 2.22, "average": 4.25, "bottom": 7.56},  # proxy: Mill Products
        "Wholesale Distribution":               {"top": 0.21, "average": 1.71, "bottom": 2.64},
    },

    "rd_expense_pct_revenue": {
        "Agriculture":                          {"top": 0.2,  "average": 1.1,  "bottom": 2.1},
        "Automotive":                           {"top": 0.5,  "average": 1.9,  "bottom": 4.2},
        "Chemical":                             {"top": 0.6,  "average": 2.9,  "bottom": 7.8},
        "Consumer Products":                    {"top": 0.3,  "average": 1.1,  "bottom": 2.1},
        "Engineering, Construction & Operations": {"top": 0.8, "average": 2.4, "bottom": 4.1},  # proxy: Industrial Manufacturing
        "High Tech":                            {"top": 3.3,  "average": 5.9,  "bottom": 10.0},
        "Industrial Manufacturing":             {"top": 0.8,  "average": 2.4,  "bottom": 4.1},
        "Life Sciences":                        {"top": 4.5,  "average": 9.1,  "bottom": 12.2},
        "Mill Products":                        {"top": 0.3,  "average": 0.9,  "bottom": 1.5},
        "Oil, Gas & Energy":                    {"top": 0.6,  "average": 2.9,  "bottom": 7.8},  # proxy: Chemical
    },

    "total_logistics_cost_pct_cogs": {
        "Agriculture":                          {"top": 7.4,  "average": 10.3, "bottom": 13.4},
        "Automotive":                           {"top": 2.9,  "average": 5.9,  "bottom": 9.4},
        "Chemical":                             {"top": 2.4,  "average": 7.1,  "bottom": 12.1},
        "Consumer Products":                    {"top": 6.6,  "average": 10.3, "bottom": 13.8},
        "Engineering, Construction & Operations": {"top": 2.1, "average": 5.6, "bottom": 7.9},   # proxy: Industrial Manufacturing
        "High Tech":                            {"top": 1.7,  "average": 5.2,  "bottom": 7.2},
        "Industrial Manufacturing":             {"top": 2.1,  "average": 5.6,  "bottom": 7.9},
        "Life Sciences":                        {"top": 3.2,  "average": 5.0,  "bottom": 6.5},
        "Mill Products":                        {"top": 4.9,  "average": 8.0,  "bottom": 10.3},
        "Oil, Gas & Energy":                    {"top": 2.4,  "average": 7.1,  "bottom": 12.1},  # proxy: Chemical
        "Professional Services":                {"top": 3.2,  "average": 5.0,  "bottom": 6.5},  # proxy: Life Sciences (already present)
        "Retail":                               {"top": 6.6,  "average": 10.3, "bottom": 13.8},  # proxy: Consumer Products
        "Telecommunications":                   {"top": 3.0,  "average": 5.2,  "bottom": 8.0},   # proxy: Wholesale Distribution
        "Travel & Transportation":              {"top": 3.0,  "average": 5.2,  "bottom": 8.0},   # proxy: Wholesale Distribution
        "Utilities":                            {"top": 2.4,  "average": 7.1,  "bottom": 12.1},  # proxy: Chemical
        "Wholesale Distribution":               {"top": 3.0,  "average": 5.2,  "bottom": 8.0},
    },

    "days_in_inventory": {
        "Agriculture":                          {"top": 50.1, "average": 83.4,  "bottom": 122.0},
        "Automotive":                           {"top": 42.6, "average": 55.7,  "bottom": 73.0},
        "Chemical":                             {"top": 50.8, "average": 74.0,  "bottom": 95.6},
        "Consumer Products":                    {"top": 46.4, "average": 74.1,  "bottom": 103.2},
        "Engineering, Construction & Operations": {"top": 5.5, "average": 31.5, "bottom": 61.9},
        "High Tech":                            {"top": 43.7, "average": 71.8,  "bottom": 98.6},
        "Industrial Manufacturing":             {"top": 48.2, "average": 76.7,  "bottom": 107.4},
        "Life Sciences":                        {"top": 101.1,"average": 144.6, "bottom": 184.3},
        "Mill Products":                        {"top": 40.5, "average": 63.9,  "bottom": 88.1},
        "Oil, Gas & Energy":                    {"top": 5.8,  "average": 30.3,  "bottom": 50.6},
        "Professional Services":                {"top": 14.6, "average": 34.2,  "bottom": 56.6},
        "Retail":                               {"top": 33.7, "average": 82.9,  "bottom": 122.8},
        "Telecommunications":                   {"top": 13.9, "average": 28.7,  "bottom": 40.6},
        "Travel & Transportation":              {"top": 5.9,  "average": 24.9,  "bottom": 45.6},
        "Utilities":                            {"top": 13.6, "average": 34.1,  "bottom": 73.0},
        "Wholesale Distribution":               {"top": 28.4, "average": 58.2,  "bottom": 84.1},
    },

    "inventory_carrying_cost_pct_revenue": {
        "Agriculture":                          {"top": 0.57, "average": 1.59, "bottom": 2.43},
        "Automotive":                           {"top": 0.83, "average": 1.53, "bottom": 2.50},
        "Chemical":                             {"top": 1.05, "average": 1.40, "bottom": 1.91},
        "Consumer Products":                    {"top": 0.76, "average": 1.62, "bottom": 2.54},
        "Engineering, Construction & Operations": {"top": 1.03, "average": 1.79, "bottom": 2.81},  # proxy: Industrial Manufacturing
        "High Tech":                            {"top": 0.25, "average": 0.76, "bottom": 1.82},
        "Industrial Manufacturing":             {"top": 1.03, "average": 1.79, "bottom": 2.81},
        "Life Sciences":                        {"top": 0.44, "average": 2.08, "bottom": 3.98},
        "Mill Products":                        {"top": 0.87, "average": 1.39, "bottom": 2.42},
        "Oil, Gas & Energy":                    {"top": 0.44, "average": 1.45, "bottom": 2.46},
        "Professional Services":                {"top": 0.67, "average": 1.18, "bottom": 1.31},
        "Retail":                               {"top": 0.80, "average": 1.77, "bottom": 2.49},
        "Telecommunications":                   {"top": 0.80, "average": 1.77, "bottom": 2.49},  # proxy: Retail
        "Travel & Transportation":              {"top": 0.80, "average": 1.77, "bottom": 2.49},  # proxy: Retail
        "Utilities":                            {"top": 0.30, "average": 1.10, "bottom": 1.49},
        "Wholesale Distribution":               {"top": 0.46, "average": 1.18, "bottom": 2.72},
    },

    "invoice_error_rate_pct": {
        "Agriculture":                          {"top": 1.4,  "average": 2.0,  "bottom": 3.0},   # proxy: Consumer Products
        "Automotive":                           {"top": 2.0,  "average": 2.6,  "bottom": 4.0},   # proxy: Industrial Manufacturing
        "Chemical":                             {"top": 2.0,  "average": 2.6,  "bottom": 4.0},   # proxy: Industrial Manufacturing
        "Consumer Products":                    {"top": 1.4,  "average": 2.0,  "bottom": 3.0},
        "Engineering, Construction & Operations": {"top": 2.0, "average": 2.6, "bottom": 4.0},  # proxy: Industrial Manufacturing
        "High Tech":                            {"top": 3.0,  "average": 5.4,  "bottom": 10.7},
        "Industrial Manufacturing":             {"top": 2.0,  "average": 2.6,  "bottom": 4.0},
        "Life Sciences":                        {"top": 3.0,  "average": 5.4,  "bottom": 10.7},  # proxy: High Tech
        "Mill Products":                        {"top": 0.2,  "average": 1.0,  "bottom": 1.2},
        "Oil, Gas & Energy":                    {"top": 2.0,  "average": 2.6,  "bottom": 4.0},   # proxy: Industrial Manufacturing
        "Professional Services":                {"top": 1.4,  "average": 2.0,  "bottom": 3.0},   # proxy: Consumer Products
        "Retail":                               {"top": 1.4,  "average": 2.0,  "bottom": 3.0},   # proxy: Consumer Products
        "Telecommunications":                   {"top": 3.0,  "average": 5.4,  "bottom": 10.7},  # proxy: High Tech
        "Travel & Transportation":              {"top": 1.4,  "average": 2.0,  "bottom": 3.0},   # proxy: Consumer Products
        "Utilities":                            {"top": 2.0,  "average": 2.6,  "bottom": 4.0},   # proxy: Industrial Manufacturing
        "Wholesale Distribution":               {"top": 0.2,  "average": 1.0,  "bottom": 1.2},   # proxy: Mill Products
    },

    "direct_material_cost_pct_mfg": {
        "Agriculture":                          {"top": 44.9, "average": 58.2, "bottom": 73.1},  # proxy: Consumer Products
        "Automotive":                           {"top": 56.0, "average": 67.8, "bottom": 77.5},
        "Chemical":                             {"top": 40.0, "average": 62.8, "bottom": 78.1},
        "Consumer Products":                    {"top": 44.9, "average": 58.2, "bottom": 73.1},
        "Engineering, Construction & Operations": {"top": 57.2, "average": 68.5, "bottom": 77.1},  # proxy: Industrial Manufacturing
        "High Tech":                            {"top": 40.0, "average": 59.3, "bottom": 74.0},
        "Industrial Manufacturing":             {"top": 57.2, "average": 68.5, "bottom": 77.1},
        "Life Sciences":                        {"top": 40.0, "average": 59.3, "bottom": 74.0},  # proxy: High Tech
        "Mill Products":                        {"top": 65.5, "average": 75.1, "bottom": 85.7},
        "Oil, Gas & Energy":                    {"top": 40.0, "average": 62.8, "bottom": 78.1},  # proxy: Chemical
        "Professional Services":                {"top": 44.9, "average": 58.2, "bottom": 73.1},  # proxy: Consumer Products
        "Retail":                               {"top": 44.9, "average": 58.2, "bottom": 73.1},  # proxy: Consumer Products
        "Telecommunications":                   {"top": 40.0, "average": 59.3, "bottom": 74.0},  # proxy: High Tech
        "Travel & Transportation":              {"top": 57.2, "average": 68.5, "bottom": 77.1},  # proxy: Industrial Manufacturing
        "Utilities":                            {"top": 40.0, "average": 62.8, "bottom": 78.1},  # proxy: Chemical
        "Wholesale Distribution":               {"top": 44.9, "average": 58.2, "bottom": 73.1},  # proxy: Consumer Products
    },
}


DIRECT_SPEND_PARAMS: dict[str, dict] = {
    "top":     {"spend_under_mgmt_pct": 88.0, "sourcing_savings_rate_pct": 5.0},
    "average": {"spend_under_mgmt_pct": 77.0, "sourcing_savings_rate_pct": 3.2},
    "bottom":  {"spend_under_mgmt_pct": 66.0, "sourcing_savings_rate_pct": 1.0},
}


def get_benchmark(kpi: str, industry: str, maturity: str) -> float | None:
    """Return benchmark value for a KPI/industry/maturity combination. None if unavailable."""
    industry_data = BENCHMARKS.get(kpi, {}).get(industry)
    if not industry_data:
        return None
    return industry_data.get(maturity)


def get_cogs_pct(industry: str, maturity: str) -> float:
    """Return COGS % of revenue for an industry/maturity."""
    data = COGS_PCT.get(industry, {})
    return data.get(maturity, data.get("average", 60.0))


def get_mfg_cost_pct(industry: str, maturity: str) -> float | None:
    """Return Manufacturing Cost % of revenue for an industry/maturity. None if unavailable."""
    data = BENCHMARKS.get("manufacturing_cost_pct_revenue", {}).get(industry)
    if not data:
        return None
    return data.get(maturity)


def get_direct_spend_params(maturity: str) -> dict:
    """Return Direct Spend Under Management % and Sourcing Savings Rate % for a maturity tier."""
    return DIRECT_SPEND_PARAMS.get(maturity, DIRECT_SPEND_PARAMS["average"])
