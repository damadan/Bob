from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal


class RawSpec(BaseModel):
    row_index: int
    name: str
    unit: Optional[str] = None
    qty: Optional[float] = None
    mark: Optional[str] = None
    source_table: Optional[str] = None
    extras: Optional[Dict[str, Any]] = None


class ParseDrawingResponse(BaseModel):
    specs: List[RawSpec]
    tables: List[Dict[str, Any]]
    notes: List[str] = Field(default_factory=list)


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

class Gap(BaseModel):
    reason: Literal["no_price","unit_mismatch","ambiguous","not_mapped"]
    item: BOMItem
    detail: Optional[str] = None

class PricedBOM(BaseModel):
    items: List[PricedItem]
    subtotal: float
    currency: str = "EUR"
    gaps: Optional[List[Gap]] = None

# Request models
class ParseDrawingRequest(BaseModel):
    file_uri: str

class ExtractBOMRequest(BaseModel):
    scope: Optional[Dict[str, Any]] = None

class PriceBOMRequest(BaseModel):
    bom: BOM
    region: str
    date: Optional[str] = None

class SuggestSubsRequest(BaseModel):
    bom: Optional[BOM] = None
    priced_bom: Optional[PricedBOM] = None
    constraints: Optional[Dict[str, Any]] = None
