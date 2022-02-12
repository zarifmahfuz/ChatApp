from datetime import datetime

def get_date_repr(dt: datetime) -> str:
    """
        Manipulates a data object to produce a standard representation for the user.
    """
    dt = dt.isoformat()
    date_time = dt.split("T")
    time = date_time[1].split(":")
    date_repr = date_time[0] + " " + time[0] + ":" + time[1]
    return date_repr
