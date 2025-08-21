from __future__ import annotations
from typing import List, Dict, Any, Optional


def suggest_substitutions(budget: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return demo substitution candidates adjusted for budget.

    Budget handling:
    * ``low`` (default) - return all candidates sorted by ascending price.
    * ``mid`` - keep only mid-priced items (50-500) and sort ascending.
    * ``high`` - prefer expensive items (>=200) sorted from most to least
      expensive.

    The function is intentionally simple and uses a static catalog so that
    tests can exercise the sorting and filtering behaviour for each budget
    level.
    """
    candidates: List[Dict[str, Any]] = [
        {"code": "SUB-LOW", "name": "Budget Material", "unit_price": 10},
        {"code": "SUB-MID-A", "name": "Standard Material A", "unit_price": 100},
        {"code": "SUB-MID-B", "name": "Standard Material B", "unit_price": 200},
        {"code": "SUB-HIGH", "name": "Premium Material", "unit_price": 1000},
    ]
    budget = (budget or "low").lower()
    if budget == "mid":
        filtered = [c for c in candidates if 50 <= c["unit_price"] <= 500]
        return sorted(filtered, key=lambda c: c["unit_price"])
    if budget == "high":
        filtered = [c for c in candidates if c["unit_price"] >= 200]
        return sorted(filtered, key=lambda c: c["unit_price"], reverse=True)
    # default low-budget behaviour
    return sorted(candidates, key=lambda c: c["unit_price"])
