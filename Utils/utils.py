# utils.py
from prettytable import PrettyTable
from datetime import datetime
import os

def display_table(rows, headers):
    """Nicely display rows in a pretty table."""
    if not rows:
        print("⚠️  No records found.")
        return
    table = PrettyTable(headers)
    for r in rows:
        table.add_row(r)
    print(table)

def format_datetime(dt):
    """Format a datetime object or string safely for display."""
    if dt is None:
        return "-"
    try:
        if isinstance(dt, str):
            # attempt to parse iso-like strings
            return dt
        return dt.strftime('%d-%b-%Y %I:%M %p')
    except Exception:
        return str(dt)

def save_receipt_text(filename, text):
    """Save receipt text to disk inside receipts/ folder."""
    os.makedirs("receipts", exist_ok=True)
    path = os.path.join("receipts", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

def build_receipt_text(patient, doctor, appointment, bill_amount=None):
    """
    Build a multi-line receipt string. Expects tuples from DB queries:
      patient: (P_ID, Name, Age, Gender, Phone, Email, Address, Date_Registered)
      doctor: (D_ID, Name, Specialization, Experience, Fees, Phone, Email, Availability, Gender, Address)
      appointment: (A_ID, P_ID, D_ID, Appointment_Date, Time_Slot, Reason, Status, Date_Created)
    """
    lines = []
    lines.append("🏥  HOSPITAL APPOINTMENT RECEIPT")
    lines.append("=" * 50)
    lines.append(f"Receipt Generated : {datetime.now().strftime('%d-%b-%Y %I:%M %p')}")
    lines.append("-" * 50)
    lines.append(f"Patient ID    : {patient[0]}")
    lines.append(f"Patient Name  : {patient[1]}")
    lines.append(f"Age / Gender  : {patient[2]} / {patient[3]}")
    lines.append(f"Phone         : {patient[4]}")
    lines.append(f"Email         : {patient[5]}")
    lines.append(f"Address       : {patient[6]}")
    lines.append("-" * 50)
    lines.append(f"Doctor        : Dr. {doctor[1]} ({doctor[2]})")
    lines.append(f"Experience    : {doctor[3]} years")
    lines.append(f"Consultation  : ₹{doctor[4]:.2f}")
    lines.append("-" * 50)
    lines.append(f"Appointment ID: {appointment[0]}")
    lines.append(f"Appointment   : {appointment[3]} | {appointment[4]}")
    lines.append(f"Reason        : {appointment[5]}")
    lines.append(f"Status        : {appointment[6]}")
    if bill_amount is not None:
        lines.append("-" * 50)
        lines.append(f"Amount Paid   : ₹{bill_amount:.2f}")
    lines.append("=" * 50)
    lines.append("Thank you for choosing our hospital ❤️")
    return "\n".join(lines)
