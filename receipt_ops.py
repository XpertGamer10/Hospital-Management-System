# receipt_ops.py
from db_setup import get_connection
from tabulate import tabulate
from datetime import datetime

def view_receipts(by_patient=None, by_doctor=None):
    """View all receipts, optionally filtered by patient or doctor."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("USE hospital")

    q = """SELECT r.Receipt_ID, r.A_ID, a.P_ID, p.Name AS Patient_Name,
                  d.Name AS Doctor_Name, r.Amount, r.Payment_Mode, r.Date_Paid
           FROM receipts r
           JOIN appointments a ON r.A_ID = a.A_ID
           JOIN patients p ON a.P_ID = p.P_ID
           JOIN doctors d ON a.D_ID = d.D_ID
           WHERE 1=1"""
    params = []
    if by_patient:
        q += " AND p.P_ID=%s"; params.append(by_patient)
    if by_doctor:
        q += " AND d.D_ID=%s"; params.append(by_doctor)
    q += " ORDER BY r.Date_Paid DESC"

    cur.execute(q, tuple(params))
    rows = cur.fetchall()

    if not rows:
        print("⚠️ No receipts found.")
    else:
        print("\n--- RECEIPT RECORDS ---")
        print(tabulate(rows, headers="keys", tablefmt="grid"))

    cur.close(); conn.close()


def delete_receipt():
    """Delete a specific receipt record."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("USE hospital")

    rid = input("Enter Receipt ID to delete: ").strip()
    cur.execute("SELECT * FROM receipts WHERE Receipt_ID=%s", (rid,))
    if not cur.fetchone():
        print("⚠️ Receipt not found.")
    else:
        cur.execute("DELETE FROM receipts WHERE Receipt_ID=%s", (rid,))
        conn.commit()
        print("✅ Receipt deleted successfully.")

    cur.close(); conn.close()


def print_receipt():
    """Print or re-generate a saved receipt by Receipt ID."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("USE hospital")

    rid = input("Enter Receipt ID: ").strip()
    cur.execute("""
        SELECT r.*, a.P_ID, p.Name AS Patient_Name, d.Name AS Doctor_Name
        FROM receipts r
        JOIN appointments a ON r.A_ID = a.A_ID
        JOIN patients p ON a.P_ID = p.P_ID
        JOIN doctors d ON a.D_ID = d.D_ID
        WHERE r.Receipt_ID=%s
    """, (rid,))
    row = cur.fetchone()

    if not row:
        print("⚠️ No receipt found.")
    else:
        text = f"""
        -------------------------------
               HOSPITAL RECEIPT
        -------------------------------
        Receipt ID   : {row['Receipt_ID']}
        Appointment ID: {row['A_ID']}
        Patient Name : {row['Patient_Name']}
        Doctor Name  : {row['Doctor_Name']}
        Amount Paid  : ₹{row['Amount']:.2f}
        Payment Mode : {row['Payment_Mode']}
        Date Paid    : {row['Date_Paid'].strftime('%Y-%m-%d %H:%M:%S')}
        -------------------------------
        THANK YOU FOR YOUR VISIT
        -------------------------------
        """
        print(text)

        fname = f"receipt_{row['Receipt_ID']}.txt"
        with open(fname, "w") as f:
            f.write(text)
        print(f"🧾 Receipt saved as: {fname}")

    cur.close(); conn.close()


def receipt_menu():
    """Admin menu for managing receipts."""
    while True:
        print("\n--- RECEIPT MANAGEMENT MENU ---")
        print("1. View All Receipts")
        print("2. View Receipts by Patient ID")
        print("3. View Receipts by Doctor ID")
        print("4. Print / Re-generate Receipt")
        print("5. Delete Receipt")
        print("6. Back to Admin Menu")

        ch = input("Choose an option: ").strip()
        if ch == '1':
            view_receipts()
        elif ch == '2':
            pid = input("Enter Patient ID: ").strip()
            view_receipts(by_patient=pid)
        elif ch == '3':
            did = input("Enter Doctor ID: ").strip()
            view_receipts(by_doctor=did)
        elif ch == '4':
            print_receipt()
        elif ch == '5':
            delete_receipt()
        elif ch == '6':
            break
        else:
            print("⚠️ Invalid choice. Please try again.")
