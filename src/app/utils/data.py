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