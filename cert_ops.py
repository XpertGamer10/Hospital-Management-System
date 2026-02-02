# cert_ops.py
from db_setup import get_connection
from datetime import datetime
from tabulate import tabulate
import os

# Folder to store certificates
CERT_FOLDER = "Certificates"
os.makedirs(CERT_FOLDER, exist_ok=True)


def build_certificate_text(cert_data):
    """Build formatted certificate text (Birth/Death)"""
    lines = [
        "-------------------------------------------",
        f"        {cert_data['Type'].upper()} CERTIFICATE        ",
        "-------------------------------------------",
        f"Certificate ID : {cert_data['Certificate_ID']}",
        f"Name           : {cert_data['Name']}",
        f"Type           : {cert_data['Type']}",
        f"Parent/Guardian: {cert_data.get('Parent_Guardian', 'N/A')}",
        f"Date of Birth  : {cert_data.get('DOB', 'N/A')}",
        f"Date of Death  : {cert_data.get('DOD', 'N/A')}",
        f"Place of Event : {cert_data.get('Place_Of_Event', 'N/A')}",
        f"Date Issued    : {cert_data.get('Date_Issued', datetime.now().strftime('%Y-%m-%d'))}",
        f"Notes          : {cert_data.get('Notes', '')}",
        "-------------------------------------------",
        "Certified by: Hospital Management System",
        "-------------------------------------------"
    ]
    return "\n".join(lines)


def save_certificate_text(cert_data):
    """Save certificate to a text file"""
    filename = os.path.join(CERT_FOLDER, f"Certificate_{cert_data['Certificate_ID']}.txt")
    with open(filename, "w") as f:
        f.write(build_certificate_text(cert_data))
    return filename


def create_certificate():
    """Create a new birth or death certificate record and generate file."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("USE hospital")

    print("\n--- CREATE CERTIFICATE ---")
    ctype = input("Certificate Type (Birth/Death): ").strip().capitalize()
    if ctype not in ('Birth', 'Death'):
        print("⚠️ Invalid certificate type.")
        return

    p_id = input("Patient ID : ").strip() or None
    name = input("Full Name: ").strip()
    dob = input("Date of Birth (YYYY-MM-DD) : ").strip() or None
    dod = None
    if ctype == 'Death':
        dod = input("Date of Death (YYYY-MM-DD): ").strip()
    parent = input("Parent/Guardian: ").strip()
    place = input("Place of Event (Hospital/Other): ").strip()
    notes = input("Additional Notes: ").strip()

    
    issued_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO certificates 
        (P_ID, Type, Name, DOB, DOD, Parent_Guardian, Place_Of_Event, Notes, Date_Issued)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (p_id, ctype, name, dob, dod, parent, place, notes, issued_date))

    conn.commit()

    cert_id = cur.lastrowid
    cur.execute("SELECT * FROM certificates WHERE Certificate_ID=%s", (cert_id,))
    cert_data = cur.fetchone()

    filepath = save_certificate_text(cert_data)
    print(f"✅ Certificate created successfully (Certificate ID = {cert_id})")
    print(f"📝 Certificate saved at: {filepath}")

    cur.close(); conn.close()


def view_certificates(by_type=None, by_patient=None):
    """View all certificates, optionally filtered by type or patient."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("USE hospital")

    q = "SELECT * FROM certificates WHERE 1=1"
    params = []
    if by_type:
        q += " AND Type=%s"; params.append(by_type)
    if by_patient:
        q += " AND P_ID=%s"; params.append(by_patient)
    q += " ORDER BY Date_Issued DESC"

    cur.execute(q, tuple(params))
    rows = cur.fetchall()

    if not rows:
        print("⚠️ No certificates found.")
    else:
        print("\n--- CERTIFICATES ---")
        print(tabulate(rows, headers="keys", tablefmt="grid"))

    cur.close(); conn.close()

def delete_certificate():
    conn = get_connection(); cur = conn.cursor()
    cid = input("Enter Certificate ID to delete: ")
    cur.execute("DELETE FROM certificates WHERE Cert_ID=%s", (cid,))
    conn.commit()
    print("✅ Certificate deleted successfully.")
    cur.close(); conn.close()
    
def search_certificate():
    """Search for a certificate by ID or Name."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("USE hospital")
    keyword = input("Enter Certificate ID or Name keyword: ").strip()
    cur.execute("""
        SELECT * FROM certificates
        WHERE Certificate_ID=%s OR Name LIKE %s
        ORDER BY Date_Issued DESC
    """, (keyword, f"%{keyword}%"))
    rows = cur.fetchall()

    if not rows:
        print("⚠️ No matching certificate found.")
    else:
        print("\n--- SEARCH RESULTS ---")
        print(tabulate(rows, headers="keys", tablefmt="grid"))

    cur.close(); conn.close()


def certificate_menu():
    """Admin menu for managing certificates."""
    while True:
        print("\n--- CERTIFICATE MANAGEMENT MENU ---")
        print("1. Create New Certificate")
        print("2. View All Certificates")
        print("3. View Certificates by Type")
        print("4. View Certificates by Patient ID")
        print("5. Search Certificate")
        print("6. Back to Admin Menu")

        ch = input("Choose an option: ").strip()
        if ch == '1':
            create_certificate()
        elif ch == '2':
            view_certificates()
        elif ch == '3':
            ctype = input("Enter Type (Birth/Death): ").strip().capitalize()
            view_certificates(by_type=ctype)
        elif ch == '4':
            pid = input("Enter Patient ID: ").strip()
            view_certificates(by_patient=pid)
        elif ch == '5':
            search_certificate()
        elif ch == '6':
            break
        else:
            print("⚠️ Invalid choice. Please try again.")
