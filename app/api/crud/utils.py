from datetime import datetime, timedelta, date
from app.api.models.base import PriceListBase

import holidays
import pytz


tz = pytz.timezone("Asia/Kuala_Lumpur")


# Get the current timestamp
def timestamp_now() -> int:
    return int(datetime_now().timestamp())


# Get the current datetime from timestamp
def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, tz)


# Get the current datetime
def datetime_now() -> datetime:
    return datetime.now(tz)


# Check if it's after trading hours
def is_after_trading_hour(db) -> bool:
    # End of KLSE's stock trading hours is 5:05pm GMT+8
    end_trading_datetime = (datetime_now()).replace(
        hour=17, minute=0, second=0, microsecond=0
    )
    current_datetime = datetime_now()
    data_timestamp = PriceListBase.get_latest_timestamp(db)
    data_datetime = (
        datetime.fromtimestamp(data_timestamp, tz) if data_timestamp else None
    )
    yesterday = current_datetime - timedelta(days=1)
    data_up_to_date = (
        data_datetime.date() == current_datetime.date()
        if current_datetime >= end_trading_datetime
        and not is_holiday(current_datetime.date())
        else data_datetime.date() == yesterday.date()
    )

    # Check if data_datetime is None
    if data_datetime is None:
        raise Exception("Data is not available")

    # Check if the current date is a weekend or holiday and data is up-to-date
    if current_datetime.weekday() >= 5 or is_holiday(current_datetime.date()):
        return True if not data_up_to_date else False

    # Check if the current date is a holiday and data is not up-to-date
    if is_holiday(yesterday.date()) and not data_up_to_date:
        return True if current_datetime >= end_trading_datetime else False

    return False


# Check if the data is up-to-date
def db_data_days_diff(days: int, data_datetime: datetime | None) -> bool:
    if data_datetime:
        current_date = datetime_now().date()
        data_date = data_datetime.date()

        while data_date < current_date:
            if data_date.weekday() < 5:  # Monday to Friday
                days -= 1
            data_date += timedelta(days=1)
        return days == 0

    return False


# Convert GMT+0 timestamp to GMT+8 timestamp
def to_local_timestamp(timestamp: float) -> int:
    # Convert GMT+0 to GMT+8
    return int(timestamp) - (3600 * 8)


def to_local_datetime_from_timestamp(timestamp: int) -> datetime:
    new_timestamp = to_local_timestamp(timestamp)
    return timestamp_to_datetime(new_timestamp)


def is_holiday(holiday_date: date) -> bool:
    my_holidays = holidays.country_holidays("MY")
    return holiday_date in my_holidays
