from __future__ import annotations
from typing import List, Optional
from rapidfuzz import process, fuzz
from loguru import logger
from app.schemas.bom import BOM, BOMItem
from app.services.catalog import MaterialCatalog

def dedupe_and_sum(items: List[BOMItem]) -> List[BOMItem]:
    key = lambda it: (it.code or it.name or "").strip().lower(), (it.unit or "").lower()
    bucket = {}
    for it in items:
        k = ( (it.code or it.name or "").strip().lower(), (it.unit or "").lower() )
        if k not in bucket:
            bucket[k] = it.model_copy()
        else:
            bucket[k].qty = (bucket[k].qty or 0) + (it.qty or 0)
    return list(bucket.values())

def map_to_catalog(bom: BOM, use_semantic: bool = True, min_ratio: int = 85) -> BOM:
    cat = MaterialCatalog()
    cat.load()
    mapped: List[BOMItem] = []
    names = [ (it.name or "").strip() for it in bom.items ]

    # Fuzzy fallback pool
    pool = []
    for row_idx, row in enumerate(cat._rows):
        pool.append(row.canonical_name)
        pool.extend(row.synonyms or [])

    for it in bom.items:
        name = (it.name or "").strip()
        code = it.code
        new_item = it.model_copy()

        # If code already present — trust it
        if code:
            mapped.append(new_item)
            continue

        # Try semantic match
        matched = None
        if use_semantic:
            row = cat.best_match(name)
            if row:
                matched = row

        # Fallback: fuzzy match on canonical/synonyms
        if matched is None and name:
            m = process.extractOne(name, pool, scorer=fuzz.WRatio)
            if m and m[1] >= min_ratio:
                # find row by matched text
                for row in cat._rows:
                    if m[0] == row.canonical_name or m[0] in (row.synonyms or []):
                        matched = row
                        break

        if matched:
            new_item.code = matched.code
            new_item.name = matched.canonical_name
            if new_item.props is None:
                new_item.props = {}
            if matched.clazz:
                new_item.props.setdefault("class", matched.clazz)
        mapped.append(new_item)

    # Deduplicate after mapping
    return BOM(items=dedupe_and_sum(mapped))
