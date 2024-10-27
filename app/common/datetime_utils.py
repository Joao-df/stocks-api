from datetime import date, datetime, timedelta


def get_yesterday() -> date:
    """Return the date representing yesterday."""
    return (datetime.now() - timedelta(1)).date()
