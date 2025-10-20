from datetime import datetime, date

def get_date_as_datetime(date_input: date | datetime) -> datetime:
    if isinstance(date_input, datetime):
        return date_input
    return datetime.combine(date_input, datetime.min.time())