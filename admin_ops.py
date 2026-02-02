# admin_ops.py
from db_setup import get_connection
from patient_ops import (
    search_patient_by_id,
    search_patient_by_name,
    register_patient
)
from doctor_ops import (
    view_doctors,
    add_doctor,
    edit_doctor,
    delete_doctor,
    view_doctor_detail
)
from appointment_ops import (
    view_all_appointments,
    view_appointments_datewise,
    delete_appointment,
    edit_appointment,
    record_payment
)
from Utils.utils import display_table
from admissions_ops import admission_menu
from cert_ops import certificate_menu
import getpass
from tabulate import tabulate

# Default admin credentials (for testing only)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


# ---------- LOGIN SECTION ----------
def admin_login():
    """Handles admin login with hidden password input"""
    print("\n--- Admin Login ---")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        print("✅ Admin login successful.")
        return True
    else:
        print("❌ Invalid admin credentials.")
        return False


# ---------- MAIN ADMIN PANEL ----------
def admin_menu():
    """Displays the main admin control panel"""
    if not admin_login():
        return

    while True:
        print("\n=== ADMIN PANEL ===")
        print("1. View all patients")
        print("2. Register new patient")
        print("3. Search patient by ID")
        print("4. Search patient by name")
        print("5. Manage doctors")
        print("6. Manage appointments")
        print("7. Record payment")
        print("8. Admission System 🏥")
        print("9. Certificates (Birth/Death)")
        print("10. Manage Admins")
        print("11. Logout")
        choice = input("Choose: ").strip()

        if choice == '1':
            view_all_patients()
        elif choice == '2':
            register_patient()  # ✅ New addition
        elif choice == '3':
            search_patient_by_id()
        elif choice == '4':
            search_patient_by_name()
        elif choice == '5':
            manage_doctors_menu()
        elif choice == '6':
            manage_appointments_menu()
        elif choice == '7':
            record_payment()
        elif choice == '8':
            admission_menu()
        elif choice == '9':
            certificate_menu()
        elif choice == '10':
            manage_admin_menu()
        elif choice == '11':
            print("🔒 Logging out admin.")
            break
        else:
            print("⚠️ Invalid choice. Try again.")


# ---------- PATIENT MANAGEMENT ----------
def view_all_patients():
    """Displays all registered patients"""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("USE hospital")
        cur.execute("SELECT * FROM patients")
        rows = cur.fetchall()
        if not rows:
            print("⚠️ No patients registered yet.")
            return
        display_table(rows, [
            "P_ID", "Name", "Age", "Gender", "Phone", "Email", "Address", "Date_Registered"
        ])
    except Exception as e:
        print("❌ Error:", e)
    finally:
        cur.close(); conn.close()


# ---------- DOCTOR MANAGEMENT ----------
def manage_doctors_menu():
    """Submenu for managing doctor records"""
    while True:
        print("\n--- Manage Doctors ---")
        print("1. Add doctor")
        print("2. View all doctors")
        print("3. View doctor detail")
        print("4. Edit doctor")
        print("5. Delete doctor")
        print("6. Back")
        ch = input("Choose: ").strip()

        if ch == '1':
            add_doctor()
        elif ch == '2':
            view_doctors()
        elif ch == '3':
            view_doctor_detail()
        elif ch == '4':
            edit_doctor()
        elif ch == '5':
            delete_doctor()
        elif ch == '6':
            break
        else:
            print("⚠️ Invalid choice.")


# ---------- APPOINTMENT MANAGEMENT ----------
def manage_appointments_menu():
    """Submenu for viewing and editing appointments"""
    while True:
        print("\n--- Manage Appointments ---")
        print("1. View all appointments")
        print("2. View appointments by date")
        print("3. Edit appointment")
        print("4. Delete appointment")
        print("5. Back")
        ch = input("Choose: ").strip()

        if ch == '1':
            view_all_appointments()
        elif ch == '2':
            view_appointments_datewise()
        elif ch == '3':
            edit_appointment()
        elif ch == '4':
            delete_appointment()
        elif ch == '5':
            break
        else:
            print("⚠️ Invalid choice.")


# ---------- ADMIN ACCOUNT MANAGEMENT ----------
def manage_admin_menu():
    """Submenu for managing admins"""
    while True:
        print("\n--- Manage Admins ---")
        print("1. Add Admin")
        print("2. View Admins")
        print("3. Edit Admin")
        print("4. Delete Admin")
        print("5. Back")
        ch = input("Choose: ").strip()

        if ch == '1':
            add_admin()
        elif ch == '2':
            view_admins()
        elif ch == '3':
            edit_admin()
        elif ch == '4':
            delete_admin()
        elif ch == '5':
            break
        else:
            print("⚠️ Invalid choice.")


def add_admin():
    conn = get_connection(); cur = conn.cursor()
    username = input("Enter new admin username: ").strip()
    password = input("Enter password: ").strip()
    fullname = input("Enter full name: ").strip()
    role = input("Enter role (SuperAdmin/Admin): ").strip().capitalize()
    cur.execute("INSERT INTO admins (Username, Password, Full_Name, Role) VALUES (%s, %s, %s, %s)",
                (username, password, fullname, role))
    conn.commit()
    print("✅ Admin added successfully.")
    cur.close(); conn.close()


def view_admins():
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM admins")
    rows = cur.fetchall()
    if not rows:
        print("⚠️ No admins found.")
    else:
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    cur.close(); conn.close()


def edit_admin():
    conn = get_connection(); cur = conn.cursor()
    admin_id = input("Enter Admin ID to edit: ").strip()
    print("Which field to update?\n1. Username\n2. Password\n3. Full Name\n4. Role")
    ch = input("Choose: ")
    fields = {'1': 'Username', '2': 'Password', '3': 'Full_Name', '4': 'Role'}
    if ch not in fields:
        print("⚠️ Invalid choice.")
        return
    new_val = input(f"Enter new {fields[ch]}: ").strip()
    cur.execute(f"UPDATE admins SET {fields[ch]}=%s WHERE Admin_ID=%s", (new_val, admin_id))
    conn.commit()
    print("✅ Admin updated successfully.")
    cur.close(); conn.close()


def delete_admin():
    conn = get_connection(); cur = conn.cursor()
    admin_id = input("Enter Admin ID to delete: ").strip()
    cur.execute("DELETE FROM admins WHERE Admin_ID=%s", (admin_id,))
    conn.commit()
    print("✅ Admin deleted successfully.")
    cur.close(); conn.close()


# ---------- PASSWORD RESET ----------
def forgot_credentials():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("USE hospital")

    print("\n--- FORGOT CREDENTIALS ---")
    username = input("Enter your username: ").strip()

    cur.execute("SELECT Security_Question, Security_Answer FROM admin WHERE Username=%s", (username,))
    row = cur.fetchone()

    if not row:
        print("⚠️ No admin found with that username.")
        return

    question, answer = row
    print(f"Security Question: {question}")
    user_ans = input("Your Answer: ").strip()

    if user_ans.lower() != (answer or "").lower():
        print("❌ Incorrect answer! Cannot reset password.")
        return

    new_pass = input("Enter new password: ").strip()
    confirm = input("Confirm new password: ").strip()

    if new_pass != confirm:
        print("⚠️ Passwords do not match.")
        return

    cur.execute("UPDATE admin SET Password=%s WHERE Username=%s", (new_pass, username))
    conn.commit()
    print("✅ Password updated successfully!")

    cur.close()
    conn.close()
