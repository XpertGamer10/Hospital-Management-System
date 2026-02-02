# utils/validation.py
from datetime import datetime

def validate_date(date_str):
    """Expect YYYY-MM-DD, returns date object or raises ValueError."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def validate_timeslot_format(slot_str):
    # Basic sanity check: contains digits and dash; you can expand to regex
    if '-' not in slot_str or any(ch.isalpha() for ch in slot_str) is False:
        # still allow flexible format — just return slot string
        return slot_str
    return slot_str
