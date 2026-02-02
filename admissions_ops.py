from db_setup import get_connection
from datetime import datetime
from tabulate import tabulate

def view_beds(show_all=False):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("USE hospital")
    if show_all:
        cur.execute("SELECT Bed_ID, Department, Bed_No, Is_Occupied, Current_P_ID FROM beds ORDER BY Department, Bed_No")
    else:
        cur.execute("SELECT Bed_ID, Department, Bed_No, Is_Occupied FROM beds WHERE Is_Occupied=0 ORDER BY Department, Bed_No")
    rows = cur.fetchall()
    if not rows:
        print("No beds found.")
    else:
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    cur.close(); conn.close()

def find_available_bed(dept):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("USE hospital")
    cur.execute("SELECT Bed_ID FROM beds WHERE Department=%s AND Is_Occupied=0 LIMIT 1", (dept,))
    r = cur.fetchone()
    cur.close(); conn.close()
    return r[0] if r else None

def admit_patient():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("USE hospital")
    pid = input("Patient ID to admit: ").strip()
    print("Departments: OPD, IPD, ICU, Emergency, Radiology, Surgery")
    dept = input("Choose Department: ").strip()
    bed_id = find_available_bed(dept)
    if not bed_id:
        print(f"❌ No free beds available in {dept}.")
        return
    notes = input("Notes (optional): ").strip()
    cur.execute("UPDATE beds SET Is_Occupied=1, Current_P_ID=%s WHERE Bed_ID=%s", (pid, bed_id))
    cur.execute("INSERT INTO admissions (P_ID, Bed_ID, Department, Notes) VALUES (%s,%s,%s,%s)", (pid, bed_id, dept, notes))
    conn.commit()
    print(f"✅ Patient {pid} admitted to Bed ID {bed_id} in {dept}.")
    cur.close(); conn.close()

def discharge_patient():
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("USE hospital")
    admission_id = input("Admission ID to discharge: ").strip()
    cur.execute("SELECT * FROM admissions WHERE Admission_ID=%s AND Status='Admitted'", (admission_id,))
    adm = cur.fetchone()
    if not adm:
        print("❌ No active admission found.")
        return
    discharge_notes = input("Discharge notes (optional): ").strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        UPDATE admissions 
        SET Status='Discharged', Discharge_Date=%s, 
            Notes=CONCAT(IFNULL(Notes,''),' | Discharge: ',%s)
        WHERE Admission_ID=%s
    """, (now, discharge_notes, admission_id))
    cur.execute("UPDATE beds SET Is_Occupied=0, Current_P_ID=NULL WHERE Bed_ID=%s", (adm['Bed_ID'],))
    conn.commit()
    print(f"✅ Admission {admission_id} discharged and bed {adm['Bed_ID']} freed.")
    cur.close(); conn.close()

def view_admissions(active_only=True):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("USE hospital")
    if active_only:
        cur.execute("""
            SELECT a.Admission_ID, a.P_ID, p.Name AS Patient, a.Department, 
                   b.Bed_No, a.Admit_Date, a.Status
            FROM admissions a
            JOIN patients p ON a.P_ID = p.P_ID
            JOIN beds b ON a.Bed_ID = b.Bed_ID
            WHERE a.Status='Admitted'
            ORDER BY a.Admit_Date
        """)
    else:
        cur.execute("""
            SELECT a.Admission_ID, a.P_ID, p.Name AS Patient, a.Department, 
                   b.Bed_No, a.Admit_Date, a.Discharge_Date, a.Status
            FROM admissions a
            JOIN patients p ON a.P_ID = p.P_ID
            JOIN beds b ON a.Bed_ID = b.Bed_ID
            ORDER BY a.Admit_Date DESC
        """)
    rows = cur.fetchall()
    if not rows:
        print("No admissions found.")
    else:
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    cur.close(); conn.close()


# ✅ This is the missing function that Admin Panel was expecting
def admission_menu():
    """Admin menu to manage admissions and beds"""
    while True:
        print("\n--- ADMISSION MANAGEMENT ---")
        print("1. View available beds")
        print("2. View all beds (occupied + free)")
        print("3. Admit patient")
        print("4. Discharge patient")
        print("5. View active admissions")
        print("6. View all admissions (history)")
        print("7. Back")
        choice = input("Choose: ").strip()

        if choice == '1':
            view_beds(False)
        elif choice == '2':
            view_beds(True)
        elif choice == '3':
            admit_patient()
        elif choice == '4':
            discharge_patient()
        elif choice == '5':
            view_admissions(True)
        elif choice == '6':
            view_admissions(False)
        elif choice == '7':
            break
        else:
            print("⚠️ Invalid choice.")
