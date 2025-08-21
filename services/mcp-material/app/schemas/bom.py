from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class BOMItem(BaseModel):
    code: Optional[str] = None
    name: str
    unit: str
    qty: float
    props: Optional[Dict[str, Any]] = None
    source: Optional[str] = None


class BOM(BaseModel):
    items: List[BOMItem] = Field(default_factory=list)


class PricedItem(BOMItem):
    unit_price: float
    currency: str = "EUR"
    price_source: Optional[str] = None
    lead_time_days: Optional[int] = None


class PricedBOM(BaseModel):
    items: List[PricedItem]
    subtotal: float
    currency: str = "EUR"
    gaps: Optional[list] = None
