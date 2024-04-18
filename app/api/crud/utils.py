from datetime import datetime, timedelta

import pytz
from sqlalchemy import func

tz = pytz.timezone("Asia/Kuala_Lumpur")


def timestamp_now() -> int:
    return int(datetime_now().timestamp())


def datetime_from_timestamp(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, tz)


def datetime_now() -> datetime:
    return datetime.now(tz)


def is_after_trading_hour(db, column_name: int) -> bool:
    # End of KLSE's stock trading hours is 5:05pm GMT+8
    end_trading_datetime = (datetime_now()).replace(
        hour=17, minute=0, second=0, microsecond=0
    )
    current_datetime = datetime_now()
    after_trading_hour = current_datetime >= end_trading_datetime

    query = db.query(func.max(column_name))

    if db_data_days_diff(query, days=0) or (
        db_data_days_diff(query, days=1) and not after_trading_hour
    ):
        return False

    return True


def db_data_days_diff(query, days) -> bool:
    data_timestamp = query.scalar()
    data_datetime = (
        datetime.fromtimestamp(data_timestamp, tz) if data_timestamp else None
    )

    if data_datetime:
        current_date = datetime.now(tz).date()
        data_date = data_datetime.date()

        while data_date < current_date:
            if data_date.weekday() < 5:  # Skip Saturdays(5) and Sundays(6)
                days -= 1
            data_date += timedelta(days=1)

        return days == 0

    return False
