from __future__ import annotations
from pathlib import Path
from typing import Dict, Optional, Iterable
import json
import time
from dataclasses import dataclass
from app.core.resource_uri import ResourceUriResolver
from loguru import logger

@dataclass(frozen=True)
class PriceRecord:
    code: str
    name: str
    unit: str
    unit_price: float
    currency: str
    lead_time_days: int | None = None
    updated: str | None = None
    source: str | None = None

class Pricebook:
    def __init__(self, region: str):
        self.region = region
        self._resolver = ResourceUriResolver()
        self._loaded_at: float | None = None
        self._by_code: Dict[str, PriceRecord] = {}
        self._by_name: Dict[str, PriceRecord] = {}

    def load(self) -> None:
        uri = f"resource://pricebook/{self.region}"
        path: Path = self._resolver.resolve(uri)
        if not path.exists():
            raise FileNotFoundError(f"Pricebook not found: {uri} -> {path}")
        by_code: Dict[str, PriceRecord] = {}
        by_name: Dict[str, PriceRecord] = {}
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    rec = PriceRecord(
                        code=row.get("code") or "",
                        name=row.get("name") or "",
                        unit=row.get("unit") or "",
                        unit_price=float(row.get("unit_price")),
                        currency=row.get("currency") or "EUR",
                        lead_time_days=row.get("lead_time_days"),
                        updated=row.get("updated"),
                        source=f"pricebook:{self.region}",
                    )
                    if rec.code:
                        by_code[rec.code] = rec
                    if rec.name:
                        by_name[rec.name.lower()] = rec
                except Exception as e:
                    logger.warning(f"Skip pricebook line: {e}")
        self._by_code = by_code
        self._by_name = by_name
        self._loaded_at = time.time()
        logger.info(f"Pricebook loaded: region={self.region}, items={len(by_code) or len(by_name)}")

    def get_by_code(self, code: str) -> Optional[PriceRecord]:
        if self._loaded_at is None:
            self.load()
        return self._by_code.get(code)

    def get_by_name(self, name: str) -> Optional[PriceRecord]:
        if self._loaded_at is None:
            self.load()
        return self._by_name.get((name or "").lower())

    def codes(self) -> Iterable[str]:
        if self._loaded_at is None:
            self.load()
        return list(self._by_code.keys())
