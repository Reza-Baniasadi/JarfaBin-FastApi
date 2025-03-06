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


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    # common aliases
    alias = {
    "ts": "timestamp",
    "open_time": "timestamp",
    "close_time": "timestamp_close",
    "symbol": "ticker",
    "pair": "ticker",
    "price": "close",
    }
    df.rename(columns={k: v for k, v in alias.items() if k in df.columns}, inplace=True)
    return df


    _TS_UNITS = {
    "s": 1,
    "ms": 1_000,
    "us": 1_000_000,
    "ns": 1_000_000_000,
    }

def _infer_ts_unit(series: pd.Series) -> Optional[str]:
    s = series.dropna().astype(float)
    if s.empty:
        return None
    m = s.median()
    if 1e9 < m < 3e1:
        return "s"
    if 1e12 < m < 3e12:
        return "m"
    if 1e15 < m < 3e15:
        return "us"
    if 1e18 < m < 3e18:
        return "ns"
        return None

def coerce_datetime(df: pd.DataFrame, time_col_candidates: Iterable[str] = ("timestamp","time","date","datetime")) -> Tuple[pd.DataFrame, Optional[str]]:
    df = df.copy()
    time_col = next((c for c in time_col_candidates if c in df.columns), None)
    inferred = None
    if time_col is None:
    # try to parse any column that looks datetime
        for c in df.columns:
            try:
                parsed = pd.to_datetime(df[c], errors="raise", utc=True)
                df.insert(0, "timestamp", parsed)
                inferred = "iso"
                break
            except Exception:
                continue
    else:
        col = df[time_col]
        if pd.api.types.is_numeric_dtype(col):
            unit = _infer_ts_unit(col)
            inferred = unit

            if unit:
                df["timestamp"] = pd.to_datetime(col, unit=unit, utc=True)
            else:
                df["timestamp"] = pd.to_datetime(col, utc=True, errors="coerce")
        else:
                df["timestamp"] = pd.to_datetime(col, utc=True, errors="coerce")
        if time_col != "timestamp":
                    pass
        if "timestamp" in df.columns:
                df = df.sort_values("timestamp").reset_index(drop=True)
                return df, inferred