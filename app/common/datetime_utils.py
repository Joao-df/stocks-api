from datetime import date, datetime, timedelta


def get_yesterday() -> date:
    return (datetime.now() - timedelta(1)).date()
