from __future__ import annotations
from dataclasses import dataclass
from io import BytesIO
from typing import Dict, Iterable, List, Literal, Optional, Tuple


import pandas as pd
import numpy as np

TimeCol = Literal["timestamp", "time", "date", "datetime"]
PriceCols = List[str]


@dataclass
class CleanReport:
    rows_in: int
    rows_out: int
    duplicates_dropped: int
    cols_before: List[str]
    cols_after: List[str]
    inferred_ts_unit: Optional[str]
    warnings: List[str]

def read_any(file_bytes: bytes, filename: str) -> pd.DataFrame:
    name = filename.lower()
    bio = BytesIO(file_bytes)
    if name.endswith(".csv") or name.endswith(".txt"):
        return pd.read_csv(bio)
    if name.endswith(".json"):
        return pd.read_json(bio, lines=True)
    if name.endswith(".parquet"):
        return pd.read_parquet(bio)
    try:
        bio.seek(0)
        return pd.read_csv(bio)
    except Exception:
        bio.seek(0)
        return pd.read_json(bio)
