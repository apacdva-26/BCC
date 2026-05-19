from __future__ import annotations
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "vd_config.json"

BUSINESS_AREAS = [
    "Asset Management",
    "Finance",
    "Manufacturing",
    "Procurement",
    "R&D",
    "Sales",
    "Supply Chain",
]

INDUSTRIES = [
    "Agriculture",
    "Automotive",
    "Chemical",
    "Consumer Products",
    "Engineering, Construction & Operations",
    "High Tech",
    "Industrial Manufacturing",
    "Life Sciences",
    "Mill Products",
    "Oil, Gas & Energy",
    "Professional Services",
    "Retail",
    "Telecommunications",
    "Travel & Transportation",
    "Utilities",
    "Wholesale Distribution",
]

DEFAULT_VALUE_DRIVERS: dict[str, list[dict]] = {
    "Procurement": [
        {"name": "Reduce Maverick Spending", "benefit_pct": 8.0, "baseline": "revenue", "baseline_pct": 0.3},
        {"name": "Improve PO Processing Efficiency", "benefit_pct": 30.0, "baseline": "revenue", "baseline_pct": 0.05},
        {"name": "Lower Supply Base Risk", "benefit_pct": 5.0, "baseline": "revenue", "baseline_pct": 0.2},
    ],
    "Asset Management": [
        {"name": "Reduce Unplanned Downtime", "benefit_pct": 15.0, "baseline": "revenue", "baseline_pct": 0.1},
        {"name": "Extend Asset Useful Life", "benefit_pct": 10.0, "baseline": "revenue", "baseline_pct": 0.08},
        {"name": "Optimize Maintenance Costs", "benefit_pct": 12.0, "baseline": "revenue", "baseline_pct": 0.07},
    ],
    "Manufacturing": [
        {"name": "Improve Overall Equipment Effectiveness", "benefit_pct": 8.0, "baseline": "revenue", "baseline_pct": 0.4},
        {"name": "Reduce Scrap & Rework", "benefit_pct": 20.0, "baseline": "revenue", "baseline_pct": 0.03},
        {"name": "Accelerate Production Planning", "benefit_pct": 25.0, "baseline": "revenue", "baseline_pct": 0.02},
    ],
    "Supply Chain": [
        {"name": "Reduce Inventory Carrying Costs", "benefit_pct": 15.0, "baseline": "revenue", "baseline_pct": 0.15},
        {"name": "Improve On-Time Delivery", "benefit_pct": 10.0, "baseline": "revenue", "baseline_pct": 0.05},
        {"name": "Lower Logistics Costs", "benefit_pct": 8.0, "baseline": "revenue", "baseline_pct": 0.1},
    ],
    "Sales": [
        {"name": "Increase Win Rate", "benefit_pct": 5.0, "baseline": "revenue", "baseline_pct": 1.0},
        {"name": "Reduce Quote-to-Cash Cycle Time", "benefit_pct": 20.0, "baseline": "revenue", "baseline_pct": 0.02},
        {"name": "Improve Customer Retention", "benefit_pct": 3.0, "baseline": "revenue", "baseline_pct": 1.0},
    ],
    "Finance": [
        {"name": "Accelerate Financial Close", "benefit_pct": 30.0, "baseline": "revenue", "baseline_pct": 0.01},
        {"name": "Reduce DSO (Days Sales Outstanding)", "benefit_pct": 10.0, "baseline": "revenue", "baseline_pct": 0.12},
        {"name": "Lower Finance Operating Costs", "benefit_pct": 15.0, "baseline": "revenue", "baseline_pct": 0.02},
    ],
    "R&D": [
        {"name": "Accelerate Time-to-Market", "benefit_pct": 10.0, "baseline": "revenue", "baseline_pct": 0.08},
        {"name": "Reduce Product Development Costs", "benefit_pct": 12.0, "baseline": "revenue", "baseline_pct": 0.06},
        {"name": "Improve R&D Resource Utilization", "benefit_pct": 15.0, "baseline": "revenue", "baseline_pct": 0.05},
    ],
}


SETTINGS_FILE = Path(__file__).parent / "settings.json"
DEFAULT_PRODUCTIVITY_PCT = 10.0


def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        return json.loads(SETTINGS_FILE.read_text())
    return {"productivity_pct": DEFAULT_PRODUCTIVITY_PCT}


def save_settings(settings: dict) -> None:
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2))


def load_config() -> dict[str, list[dict]]:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return DEFAULT_VALUE_DRIVERS


def save_config(config: dict[str, list[dict]]) -> None:
    DATA_FILE.write_text(json.dumps(config, indent=2))
