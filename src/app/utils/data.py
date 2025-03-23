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

_NUMERIC_HINTS = ("open","high","low","close","price","volume","quote_volume","base_volume","wap")

def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for c in df.columns:
             if any(h in c for h in _NUMERIC_HINTS):
                df[c] = pd.to_numeric(df[c], errors="coerce")
                return df
             
def normalize_tickers(df: pd.DataFrame, mapping: Optional[Dict[str,str]] = None, base_quote_sep: Optional[str] = None) -> pd.DataFrame:
    df = df.copy()
    if "ticker" in df.columns:
        df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    if base_quote_sep and base_quote_sep in df["ticker"].iloc[0]:
     df["ticker"] = df["ticker"].str.replace(base_quote_sep, "", regex=False)
    if mapping:
        df["ticker"] = df["ticker"].map(lambda x: mapping.get(x, x))
    return df

# this function for drop dupes
def drop_dupes(df: pd.DataFrame, keys: Optional[List[str]] = None) -> Tuple[pd.DataFrame, int]:
    df = df.copy()
    keys = keys or [c for c in ("timestamp","ticker") if c in df.columns] or df.columns.tolist()
    before = len(df)
    df = df.drop_duplicates(subset=keys)
    return df, before - len(df)


def fill_missing_ohlcv(df: pd.DataFrame, freq: str = "1min", method: Literal["ffill","bfill","none"] = "ffill") -> pd.DataFrame:
    if "timestamp" not in df.columns:
        return df
    df = df.set_index("timestamp").sort_index()
    agg = {c: ("sum" if "volume" in c else "last") for c in df.columns}
    out = df.resample(freq).agg(agg)
    if method != "none":
        out = out.fillna(method=method)
    out = out.reset_index()
    return out


def detect_outliers_iqr(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            continue
    q1, q3 = df[c].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
    mask = (df[c] < lo) | (df[c] > hi)
    df.loc[mask, c] = np.nan
    return df

def validate_schema(df: pd.DataFrame, required: Iterable[str]) -> List[str]:
    miss = [c for c in required if c not in df.columns]
    return miss


def to_parquet_bytes(df: pd.DataFrame) -> bytes:
    bio = BytesIO()
    df.to_parquet(bio, index=False)
    return bio.getvalue()


def clean_crypto_df(
    df: pd.DataFrame,
    *,
    symbol_map: Optional[Dict[str,str]] = None,
    base_quote_sep: Optional[str] = "/",
    resample_to: Optional[str] = None,
    outlier_cols: Optional[Iterable[str]] = ("open","high","low","close","volume"),
    freq_fill: Literal["ffill","bfill","none"] = "ffill",
    ) -> Tuple[pd.DataFrame, CleanReport]:
    warnings: List[str] = []
    rows_in = len(df)
    cols_before = df.columns.tolist()
    df = standardize_columns(df)

    df, inferred = coerce_datetime(df)
    if inferred is None:
        warnings.append("زمان‌بندی پیدا نشد یا نامشخص بود؛ سعی شد تبدیل مستقیم انجام شود.")
    df = coerce_numeric(df)
    df = normalize_tickers(df, symbol_map, base_quote_sep)
    df, dups = drop_dupes(df)

    required = [c for c in ("timestamp","open","high","low","close","volume") if c in df.columns or c != "timestamp"]
    miss = validate_schema(df, required=["timestamp"])
    if miss:
        warnings.append(f"ستون‌های ضروری یافت نشد: {miss}")
    if outlier_cols:
        df = detect_outliers_iqr(df, [c for c in outlier_cols if c in df.columns])
    
    if resample_to:
        try:
            df = fill_missing_ohlcv(df, resample_to, method=freq_fill)
        except Exception as e:
            warnings.append(f"خطای بازنمونه‌گیری: {e}")


        report = CleanReport(
        rows_in=rows_in,
        rows_out=len(df),
        duplicates_dropped=dups,
        cols_before=cols_before,
        cols_after=df.columns.tolist(),
        inferred_ts_unit=inferred,
       )
        return df, report