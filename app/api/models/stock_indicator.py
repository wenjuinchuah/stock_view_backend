from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Indicator(Enum):
    CCI = "cci"
    MACD = "macd"
    KDJ = "kdj"


class CCIIndicator(BaseModel):
    time_period: int | None = 20
    overbought: int | None = 100
    oversold: int | None = -100


class MACDIndicator(BaseModel):
    fast_period: int | None = 12
    slow_period: int | None = 26
    signal_period: int | None = 9


class KDJIndicator(BaseModel):
    loopback_period: int | None = 9
    signal_period: int | None = 3
    smooth_period: int | None = 3


class StockIndicator(BaseModel):
    cci: Optional["CCIIndicator"] = None
    macd: Optional["MACDIndicator"] = None
    kdj: Optional["KDJIndicator"] = None
    # name: Indicator
    # # CCI
    # time_period: int | None = 20
    # overbought: int | None = 100
    # oversold: int | None = -100
    # # MACD
    # fast_period: int | None = 12
    # slow_period: int | None = 26
    # signal_period: int | None = None  # default 9 for MACD, 3 for KDJ, None for CCI
    # # KDJ
    # loopback_period: int | None = 9
    # smooth_period: int | None = 3
