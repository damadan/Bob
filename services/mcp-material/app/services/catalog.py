from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json
import os
from dataclasses import dataclass
import numpy as np
from loguru import logger

from app.core.config import settings
from app.core.resource_uri import ResourceUriResolver

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    HAS_EMB = True
except Exception:
    HAS_EMB = False

@dataclass
class MaterialRow:
    code: str
    canonical_name: str
    clazz: Optional[str]
    props: Dict
    synonyms: List[str]

class MaterialCatalog:
    def __init__(self):
        self._resolver = ResourceUriResolver()
        self._rows: List[MaterialRow] = []
        self._emb_model: Optional[SentenceTransformer] = None
        self._index = None
        self._texts: List[str] = []  # text to embed
        self._by_code: Dict[str, int] = {}
        self._loaded = False

    def _load_rows(self) -> None:
        path = self._resolver.resolve("resource://catalog/materials")
        with path.open("r", encoding="utf-8") as fh:
            rows = []
            by_code = {}
            for i, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                mr = MaterialRow(
                    code=row["code"],
                    canonical_name=row.get("canonical_name") or row.get("name") or "",
                    clazz=(row.get("class") or row.get("clazz")),
                    props=row.get("props") or {},
                    synonyms=row.get("synonyms") or [],
                )
                by_code[mr.code] = len(rows)
                rows.append(mr)
            self._rows = rows
            self._by_code = by_code

    def _ensure_model(self):
        """Load embedding model if available, otherwise disable semantic matching.

        The embedding stack (sentence-transformers + model weights) might not be
        available in restricted environments. Instead of raising and breaking the
        service we fall back to a fuzzy matcher only.  Any failure while loading
        the model will flip the global ``HAS_EMB`` flag so subsequent calls know
        semantic search is disabled.
        """

        global HAS_EMB

        if self._emb_model is not None:
            return
        if not HAS_EMB:
            return
        try:
            self._emb_model = SentenceTransformer(settings.CATALOG_MODEL_NAME)
        except Exception as exc:
            # Loading can fail when the model is missing or network access is
            # blocked.  Log and disable semantic matching gracefully.
            logger.warning(f"Failed to load embeddings model: {exc}")
            self._emb_model = None
            HAS_EMB = False

    def _build_texts(self) -> List[str]:
        texts = []
        for r in self._rows:
            # concatenate canonical and synonyms
            all_aliases = [r.canonical_name] + list(r.synonyms or [])
            # add class/props tokens (weak signals)
            if r.clazz:
                all_aliases.append(str(r.clazz))
            if r.props:
                all_aliases.extend([f"{k}:{v}" for k, v in r.props.items()])
            texts.append(" | ".join(all_aliases))
        self._texts = texts
        return texts

    def _index_paths(self) -> Tuple[Path, Path]:
        faiss_path = settings.CATALOG_INDEX_PATH
        emb_meta_path = settings.CATALOG_EMB_PATH
        return (faiss_path, emb_meta_path)

    def load(self, rebuild: bool = False) -> None:
        if self._loaded and not rebuild:
            return
        self._load_rows()
        # Always attempt to initialise the embedding model.  _ensure_model will
        # disable HAS_EMB if loading fails (e.g. no network / missing weights).
        self._ensure_model()
        if not HAS_EMB or self._emb_model is None:
            logger.warning("Embeddings stack not available; semantic match disabled")
            self._loaded = True
            return

        faiss_path, emb_meta_path = self._index_paths()
        if (not rebuild) and faiss_path.exists() and emb_meta_path.exists():
            # fast load
            self._ensure_model()
            self._index = faiss.read_index(str(faiss_path))
            with emb_meta_path.open("r", encoding="utf-8") as fh:
                meta = json.load(fh)
            self._texts = meta["texts"]
            logger.info(f"Loaded FAISS index: {faiss_path}")
        else:
            # build
            self._ensure_model()
            texts = self._build_texts()
            X = self._emb_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            d = X.shape[1]
            index = faiss.IndexFlatIP(d)
            index.add(X.astype(np.float32))
            self._index = index
            faiss.write_index(index, str(faiss_path))
            with emb_meta_path.open("w", encoding="utf-8") as fh:
                json.dump({"texts": texts}, fh, ensure_ascii=False, indent=2)
            logger.info(f"Built and saved FAISS index: {faiss_path}")
        self._loaded = True

    def match(self, query: str, top_k: int = None) -> List[Tuple[int, float]]:
        if not self._loaded:
            self.load()
        if not HAS_EMB or self._index is None or not query:
            return []
        top_k = top_k or settings.CATALOG_TOPK
        q = self._emb_model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
        scores, ids = self._index.search(q, top_k)
        out = []
        for i, s in zip(ids[0], scores[0]):
            if i < 0:
                continue
            out.append((int(i), float(s)))
        return out

    def resolve_row(self, idx: int) -> MaterialRow:
        return self._rows[idx]

    def best_match(self, query: str, min_score: float = None) -> Optional[MaterialRow]:
        min_score = min_score or settings.CATALOG_MIN_SCORE
        candidates = self.match(query, top_k=settings.CATALOG_TOPK)
        if not candidates:
            return None
        idx, score = candidates[0]
        if score < min_score:
            return None
        return self._rows[idx]
