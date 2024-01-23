class Response:
    @staticmethod
    def error(e: Exception | None = None) -> dict:
        return {
            "status": "ERROR",
            "message": str(e) if e else "Something went wrong",
        }

    @staticmethod
    def success(o: object | dict | str | None = None) -> dict:
        if isinstance(o, dict):
            pass
        elif isinstance(o, str):
            o = {"message": o}
        elif isinstance(o, object) and o is not None:
            o = o.__dict__
        return {
            "status": "SUCCESS",
            "data": o if o else None,
        }


class Indicator:
    CCI = "cci"
    MACD = "macd"


class Page:
    rows_per_page = 100
