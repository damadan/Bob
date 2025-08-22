from pathlib import Path
from typing import Dict, Any, List
try:
    import ifcopenshell
    import ifcopenshell.util.element as ifcutil
except Exception:
    ifcopenshell = None

from app.schemas.bom import RawSpec
from app.core.metrics import PARSE_ROWS

ELEMENT_CLASSES = [
    "IfcWall", "IfcSlab", "IfcDoor", "IfcWindow", "IfcColumn", "IfcBeam"
]

def parse_ifc_to_specs(ifc_path: Path) -> Dict[str, Any]:
    if ifcopenshell is None:
        # Library not available: return empty with a note
        return {"specs": [], "tables": [], "notes": ["ifcopenshell not installed"]}

    model = ifcopenshell.open(str(ifc_path))
    specs: List[RawSpec] = []

    for cls in ELEMENT_CLASSES:
        try:
            for el in model.by_type(cls) or []:
                name = (el.Name or cls)
                unit = None
                qty = None
                # BaseQuantities: try common fields
                try:
                    psets = ifcutil.get_psets(el, psets_only=True)
                except Exception:
                    psets = {}
                bq = psets.get("BaseQuantities") or {}
                # prefer Volume > Area > Length > Count
                qty = bq.get("NetVolume") or bq.get("GrossVolume") or bq.get("NetArea") or bq.get("GrossArea") or bq.get("Length") or bq.get("Count")
                unit = "m3" if "Volume" in (bq and "".join(bq.keys()) or "") else ("m2" if "Area" in (bq and "".join(bq.keys()) or "") else ("m" if "Length" in (bq and "".join(bq.keys()) or "") else ("pcs" if "Count" in (bq and "".join(bq.keys()) or "") else None)))
                try:
                    qty = float(qty) if qty is not None else None
                except Exception:
                    qty = None

                specs.append(RawSpec(
                    row_index=0,
                    name=str(name),
                    unit=unit,
                    qty=qty,
                    mark=None,
                    source_table=f"{cls}",
                    extras={"GlobalId": getattr(el, "GlobalId", None)}
                ))
                PARSE_ROWS.labels(engine="ifc").inc()
        except Exception:
            continue

    return {
        "specs": [s.model_dump() for s in specs],
        "tables": [],
        "notes": [],
    }
