from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Indicator(Enum):
    CCI = "cci"
    MACD = "macd"
    KDJ = "kdj"
    # TODO: Add new indicator here


class CCIIndicator(BaseModel):
    time_period: int | None = 20
    overbought: int | None = 100
    oversold: int | None = -100


class MACDIndicator(BaseModel):
    fast_period: int | None = 12
    slow_period: int | None = 26
    signal_period: int | None = 9
    bearish: bool | None = False
    bullish: bool | None = False


class KDJIndicator(BaseModel):
    loopback_period: int | None = 9
    signal_period: int | None = 3
    smooth_period: int | None = 3
    golden_cross: bool | None = False
    death_cross: bool | None = False


# TODO: Add new indicator here


class StockIndicator(BaseModel):
    cci: Optional["CCIIndicator"] = None
    macd: Optional["MACDIndicator"] = None
    kdj: Optional["KDJIndicator"] = None
    # TODO: Add new indicator here
