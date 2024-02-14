from datetime import datetime, timedelta

import pytz

tz = pytz.timezone("Asia/Kuala_Lumpur")


def timestamp_now() -> int:
    return int(datetime.now(tz).timestamp())


def datetime_now_from_timestamp(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, tz).date()


def datetime_now() -> datetime:
    return datetime.now(tz).date()


def is_after_trading_hour() -> bool:
    # End of KLSE's stock trading hours is 12am GMT+8
    end_trading_hour = (
        datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0).time()
    )
    current_time = datetime.now(tz).time()
    return current_time >= end_trading_hour


def db_data_days_diff(query, days) -> bool:
    data_timestamp = query.scalar()
    data_datetime = (
        datetime.fromtimestamp(data_timestamp, tz) if data_timestamp else None
    )

    return data_datetime and data_datetime.date() - datetime.now(
        tz
    ).date() == timedelta(days)
