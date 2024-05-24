from datetime import datetime, timedelta, date

import holidays
import pytz
from sqlalchemy import func

tz = pytz.timezone("Asia/Kuala_Lumpur")


# Get the current timestamp
def timestamp_now() -> int:
    return int(datetime_now().timestamp())


# Get the current datetime from timestamp
def datetime_from_timestamp(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, tz)


# Get the current datetime
def datetime_now() -> datetime:
    return datetime.now(tz)


# Check if it's after trading hours
def is_after_trading_hour(db, column_name: int) -> bool:
    # End of KLSE's stock trading hours is 5:05pm GMT+8
    end_trading_datetime = (datetime_now()).replace(
        hour=17, minute=0, second=0, microsecond=0
    )
    current_datetime = datetime_now()
    query = db.query(func.max(column_name))
    data_timestamp = query.scalar()
    data_datetime = (
        datetime.fromtimestamp(data_timestamp, tz) if data_timestamp else None
    )

    # Check if data_datetime is None
    if data_datetime is None:
        return False

    # Check if data_datetime is from the previous day
    yesterday = current_datetime - timedelta(days=1)
    if data_datetime.date() == yesterday.date():
        # If it's after trading hours and yesterday was a weekday, return True
        if (
            current_datetime > end_trading_datetime
            and yesterday.weekday() < 5
            and not is_holiday(yesterday.date())
        ):
            return True

    # If data_datetime is not from the previous day, return True regardless of the current time
    elif data_datetime.date() != current_datetime.date() and not is_holiday(
        yesterday.date()
    ):
        return True

    # If it's the weekend, return False
    if current_datetime.weekday() in [5, 6]:  # Saturday or Sunday
        return False

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
    return datetime_from_timestamp(new_timestamp)


def is_holiday(holiday_date: date) -> bool:
    print(f"Checking if {holiday_date} is a holiday")
    my_holidays = holidays.country_holidays("MY")
    print(f"is_holiday: {holiday_date in my_holidays}")
    return holiday_date in my_holidays
