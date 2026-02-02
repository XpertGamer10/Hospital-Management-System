# billing_ops.py
from db_setup import get_connection
from datetime import datetime
import uuid

def _generate_bill_no(conn):
    # Format: BILL-YYYYMMDD-XXXX (incremental-like using UUID short part to avoid race)
    today = datetime.now().strftime("%Y%m%d")
    short = uuid.uuid4().hex[:6].upper()
    return f"BILL-{today}-{short}"

def record_payment():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("USE hospital")
    print("\n--- Record Payment ---")
    aid = input("Appointment ID (optional, press Enter if none): ").strip() or None
    pid = input("Patient ID: ").strip()
    amount = float(input("Amount (INR): ").strip())
    mode = input("Payment Mode (Cash/Card/UPI): ").strip().capitalize() or "Cash"
    notes = input("Notes (optional): ").strip()

    bill_no = _generate_bill_no(conn)
    cur.execute("""
        INSERT INTO receipts (A_ID, P_ID, Bill_No, Amount, Payment_Mode, Notes)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (aid, pid, bill_no, amount, mode, notes))
    conn.commit()
    print(f"✅ Payment recorded. Receipt ID: {cur.lastrowid} | Bill No: {bill_no}")
    cur.close(); conn.close()
    return cur.lastrowid

def print_receipt(receipt_id=None, bill_no=None):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("USE hospital")
    if receipt_id:
        cur.execute("SELECT * FROM receipts WHERE Receipt_ID=%s", (receipt_id,))
    elif bill_no:
        cur.execute("SELECT * FROM receipts WHERE Bill_No=%s", (bill_no,))
    else:
        print("Provide receipt_id or bill_no")
        return
    r = cur.fetchone()
    if not r:
        print("Receipt not found.")
        return
    # fetch patient and appointment info
    cur.execute("SELECT Name, Age, Phone_No, Email FROM patients WHERE P_ID=%s", (r['P_ID'],))
    p = cur.fetchone()
    print("\n------ RECEIPT ------")
    print(f"Bill No : {r['Bill_No']}")
    print(f"Receipt ID : {r['Receipt_ID']}")
    if p:
        print(f"Patient : {p[0]} | Age: {p[1]} | Phone: {p[2]} | Email: {p[3]}")
    print(f"Amount : ₹{r['Amount']:.2f}")
    print(f"Payment Mode : {r['Payment_Mode']}")
    print(f"Date Paid : {r['Date_Paid']}")
    print(f"Notes : {r['Notes']}")
    print("---------------------\n")
    cur.close(); conn.close()

def search_receipts(by_name=None, by_date=None, sort_by='Date_Paid', asc=True):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("USE hospital")
    q = """
        SELECT r.Receipt_ID, r.Bill_No, r.Amount, r.Payment_Mode, r.Date_Paid, p.Name AS Patient
        FROM receipts r
        JOIN patients p ON r.P_ID = p.P_ID
    """
    params = []
    where = []
    if by_name:
        where.append("p.Name LIKE %s"); params.append(f"%{by_name}%")
    if by_date:
        # by_date can be 'YYYY-MM-DD' or tuple(start,end)
        if isinstance(by_date, tuple):
            where.append("DATE(r.Date_Paid) BETWEEN %s AND %s"); params.extend(by_date)
        else:
            where.append("DATE(r.Date_Paid) = %s"); params.append(by_date)
    if where:
        q += " WHERE " + " AND ".join(where)
    q += f" ORDER BY {sort_by} {'ASC' if asc else 'DESC'}"
    cur.execute(q, tuple(params))
    rows = cur.fetchall()
    if not rows:
        print("No receipts found.")
    else:
        from tabulate import tabulate
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    cur.close(); conn.close()
