# patient_ops.py
from db_setup import get_connection
from Utils.utils import display_table, format_datetime, build_receipt_text, save_receipt_text
from datetime import datetime

def register_patient():
    print("\n--- Register New Patient ---")
    name = input("Name: ").strip()
    age = input("Age: ").strip()
    gender = input("Gender (Male/Female/Other): ").strip().capitalize()
    phone = input("Phone No: ").strip()
    email = input("Email: ").strip()
    address = input("Address: ").strip()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("USE hospital")
        cur.execute("""
            INSERT INTO patients (Name, Age, Gender, Phone_No, Email, Address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, age, gender, phone, email, address))
        conn.commit()
        pid = cur.lastrowid
        print(f"✅ Patient registered (P_ID={pid})")
    except Exception as e:
        print("❌ Error registering patient:", e)
    finally:
        cur.close()
        conn.close()

def search_patient_by_id():
    pid = input("Enter Patient ID: ").strip()
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("USE hospital")
        cur.execute("SELECT * FROM patients WHERE P_ID = %s", (pid,))
        r = cur.fetchone()
        if r:
            print("\n------------------ PATIENT DETAILS ------------------")
            print(f"🧾 Patient ID     : {r[0]}")
            print(f"👤 Name           : {r[1]}")
            print(f"🎂 Age            : {r[2]}")
            print(f"⚧ Gender         : {r[3]}")
            print(f"📞 Phone Number   : {r[4]}")
            print(f"📧 Email          : {r[5]}")
            print(f"🏠 Address        : {r[6]}")
            print(f"📅 Registered On  : {format_datetime(r[7])}")
            print("--------------------------------------------------")
        else:
            print("⚠️ No patient found with that ID.")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        cur.close(); conn.close()

def search_patient_by_name():
    name = input("Enter name (partial allowed): ").strip()
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("USE hospital")
        cur.execute("SELECT * FROM patients WHERE Name LIKE %s", (f"%{name}%",))
        rows = cur.fetchall()
        if not rows:
            print("⚠️ No patients found.")
            return
        for i, r in enumerate(rows, start=1):
            print(f"\n🔹 Record {i}")
            print(f"ID    : {r[0]}")
            print(f"Name  : {r[1]}")
            print(f"Age   : {r[2]}")
            print(f"Gender: {r[3]}")
            print(f"Phone : {r[4]}")
            print(f"Email : {r[5]}")
            print(f"Address: {r[6]}")
            print(f"Registered On: {format_datetime(r[7])}")
            print("-" * 50)
    except Exception as e:
        print("❌ Error:", e)
    finally:
        cur.close(); conn.close()

def view_my_appointments():
    """
    View appointments for one patient only. Patient identifies themselves by ID or phone.
    """
    print("\n--- View My Appointments ---")
    pid = input("Enter your Patient ID (or press Enter to use Phone): ").strip()
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("USE hospital")
        if not pid:
            phone = input("Enter your registered Phone Number: ").strip()
            cur.execute("SELECT P_ID FROM patients WHERE Phone_No = %s", (phone,))
            res = cur.fetchone()
            if not res:
                print("⚠️ No patient found with that phone number.")
                return
            pid = res[0]

        # fetch appointments
        cur.execute("""
            SELECT a.A_ID, p.Name, d.Name, d.Specialization, a.Appointment_Date, a.Time_Slot, a.Reason, a.Status
            FROM appointments a
            JOIN patients p ON a.P_ID = p.P_ID
            JOIN doctors d ON a.D_ID = d.D_ID
            WHERE a.P_ID = %s
            ORDER BY a.Appointment_Date, a.Time_Slot
        """, (pid,))
        rows = cur.fetchall()
        if not rows:
            print("⚠️ You have no appointments.")
            return

        for r in rows:
            print("\n📌 Appointment")
            print(f"Appointment ID : {r[0]}")
            print(f"Patient Name   : {r[1]}")
            print(f"Doctor         : Dr. {r[2]} ({r[3]})")
            print(f"Date & Time    : {r[4]} | {r[5]}")
            print(f"Reason         : {r[6]}")
            print(f"Status         : {r[7]}")
            print("-" * 50)
    except Exception as e:
        print("❌ Error:", e)
    finally:
        cur.close(); conn.close()

def print_receipt_by_appointment():
    """
    Print and save a receipt for a given appointment ID.
    """
    aid = input("Enter Appointment ID: ").strip()
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("USE hospital")
        # fetch appointment
        cur.execute("SELECT * FROM appointments WHERE A_ID = %s", (aid,))
        appointment = cur.fetchone()
        if not appointment:
            print("⚠️ No appointment found with that ID.")
            return
        # fetch patient and doctor
        cur.execute("SELECT * FROM patients WHERE P_ID = %s", (appointment[1],))
        patient = cur.fetchone()
        cur.execute("SELECT * FROM doctors WHERE D_ID = %s", (appointment[2],))
        doctor = cur.fetchone()

        # fetch billing if any
        cur.execute("SELECT Amount FROM billing WHERE A_ID = %s ORDER BY Date_Paid DESC LIMIT 1", (aid,))
        bill = cur.fetchone()
        bill_amount = bill[0] if bill else None

        text = build_receipt_text(patient, doctor, appointment, bill_amount)
        print("\n" + text + "\n")
        # save to file
        filename = f"receipt_A{aid}_P{patient[0]}.txt"
        path = save_receipt_text(filename, text)
        print(f"✅ Receipt saved at: {path}")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        cur.close(); conn.close()

def delete_patient():
    conn = get_connection(); cur = conn.cursor()
    pid = input("Enter Patient ID to delete: ")
    cur.execute("DELETE FROM patients WHERE P_ID=%s", (pid,))
    conn.commit()
    print("✅ Patient deleted successfully.")
    cur.close(); conn.close()