from datetime import datetime, timedelta, date

import pytz

tz = pytz.timezone("Asia/Kuala_Lumpur")


def timestamp_now() -> int:
    return int(datetime.now(tz).timestamp())


def date_now_from_timestamp(timestamp: int) -> date:
    return datetime.fromtimestamp(timestamp, tz).date()


def date_now() -> date:
    return datetime.now(tz).date()


def is_after_trading_hour() -> bool:
    # End of KLSE's stock trading hours is next day 12am GMT+8
    end_trading_datetime = (datetime.now(tz) + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    current_datetime = datetime.now(tz)
    return current_datetime >= end_trading_datetime


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
