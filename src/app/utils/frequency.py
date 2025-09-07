import pandas as pd
from __future__ import annotations
from typing import Iterable, Tuple, Dict, Optional
import pandas as pd
import numpy as np
from io import BytesIO


def detect_freq(df: pd.DataFrame, time_col: str = "timestamp") -> Optional[str]:
    if time_col not in df.columns:
        return None
    s = pd.to_datetime(df[time_col], utc=True, errors="coerce").dropna().sort_values()
    if len(s) < 3:
        return None
    deltas = (s.iloc[1:].values - s.iloc[:-1].values).astype("timedelta64[s]").astype(int)
    if len(deltas) == 0:
        return None
    sec = int(pd.Series(deltas).mode().iloc[0])
    mapping = {1:"1s", 5:"5s", 15:"15s", 30:"30s", 60:"1min", 120:"2min", 300:"5min", 900:"15min", 1800:"30min", 3600:"1H", 86400:"1D"}
    return mapping.get(sec, f"{sec}s")