from datetime import datetime, timedelta, date
from app.api.models.base import PriceListBase

import holidays
import pytz


tz = pytz.timezone("Asia/Kuala_Lumpur")


# Get the current timestamp
def timestamp_now() -> int:
    return int(datetime_now().timestamp())


def datetime_to_timestamp(date_time: datetime) -> int:
    return date_time.timestamp().__int__()


# Get the current datetime from timestamp
def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, tz)


# Get the current datetime
def datetime_now() -> datetime:
    return datetime.now(tz)


# Check if it's after trading hours
def is_after_trading_hour(db) -> bool:
    # End of KLSE's stock trading hours is 5:00pm GMT+8
    end_trading_datetime = (datetime_now()).replace(
        hour=17, minute=0, second=0, microsecond=0
    )
    current_datetime = datetime_now()  # GMT+8

    data_timestamp = PriceListBase.get_latest_timestamp(db)  # GMT+0
    data_datetime = (
        to_local_datetime_from_timestamp(data_timestamp) if data_timestamp else None
    )  # GMT+8

    yesterday_datetime = current_datetime - timedelta(days=1)  # GMT+8

    # Check if data is up-to-date
    data_up_to_date = (
        data_datetime.date() == current_datetime.date()
        if current_datetime >= end_trading_datetime
        and not is_holiday(current_datetime.date())
        and current_datetime.weekday() < 5
        else data_datetime.date() == yesterday_datetime.date()
        or data_datetime.date() == (current_datetime.date() - timedelta(days=2))
    )

    # Check if data_datetime is None
    if data_datetime is None:
        raise Exception("Data is not available")

    if data_up_to_date:
        return False

    # For the following, the data is not up-to-date
    yesterday_is_holiday = is_holiday(yesterday_datetime.date())
    today_is_holiday = is_holiday(current_datetime.date())
    today_is_weekend = current_datetime.weekday() >= 5

    # Return True even if yesterday or today is holiday or today is weekend
    if yesterday_is_holiday or today_is_holiday or today_is_weekend:
        return True

    # Return True if not all of the above conditions are met and current_datetime is after trading hour
    return True if current_datetime >= end_trading_datetime else False


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
