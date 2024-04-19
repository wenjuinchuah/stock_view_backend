class Response:
    @staticmethod
    def error(e: Exception | None = None) -> dict:
        return {
            "status": "ERROR",
            "message": str(e) if e else "Something went wrong",
        }

    @staticmethod
    def success(o: object | dict | str | None = None) -> dict:
        if isinstance(o, dict) or isinstance(o, list):
            pass
        elif isinstance(o, str):
            o = {"message": o}
        elif isinstance(o, bool):
            o = o
        elif isinstance(o, object) and o is not None:
            o = o.__dict__
        return {
            "status": "SUCCESS",
            "data": o,
        }


class Page:
    rows_per_page = 100


class TimePeriod:
    one_month = "1M"
    three_months = "3M"
    six_months = "6M"
    one_year = "1Y"
    five_years = "5Y"
    all = "ALL"
