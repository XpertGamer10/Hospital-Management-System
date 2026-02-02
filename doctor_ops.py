# doctor_ops.py
import json
from tabulate import tabulate
from db_setup import get_connection


# ---------------------------------------------------------
# Add a new doctor
# ---------------------------------------------------------
def add_doctor():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("USE hospital")

    print("\n--- Add New Doctor ---")
    name = input("Name: ").strip()
    specialization = input("Specialization: ").strip()
    experience = input("Experience (years): ").strip()
    fees = input("Consultation Fees: ").strip()
    phone = input("Phone No: ").strip()
    email = input("Email: ").strip()
    gender = input("Gender (Male/Female/Other): ").strip()
    address = input("Address: ").strip()

    # Availability input
    print("\nEnter availability schedule (day and slots). Leave blank to stop.")
    availability = {}
    while True:
        day = input("Day (e.g., Monday): ").strip()
        if not day:
            break
        slots = input(f"Enter time slots for {day} (comma-separated): ").split(",")
        availability[day] = [s.strip() for s in slots if s.strip()]

    try:
        cur.execute("""
            INSERT INTO doctors
            (Name, Specialization, Experience, Fees, Phone_No, Email, Availability, Gender, Address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name, specialization, experience, fees, phone, email,
            json.dumps(availability), gender, address
        ))
        conn.commit()
        print(f"✅ Doctor added successfully (D_ID = {cur.lastrowid})")
    except Exception as e:
        print("❌ Error adding doctor:", e)
    finally:
        cur.close()
        conn.close()


# ---------------------------------------------------------
# View all doctors (summary table)
# ---------------------------------------------------------
def view_doctors():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("USE hospital")

    cur.execute("SELECT D_ID, Name, Specialization, Experience, Fees, Phone_No, Email FROM doctors")
    rows = cur.fetchall()

    if not rows:
        print("⚠️ No doctors found.")
    else:
        headers = ["D_ID", "Name", "Specialization", "Experience", "Fees", "Phone", "Email"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    cur.close()
    conn.close()


# ---------------------------------------------------------
# View detailed info for one doctor
# ---------------------------------------------------------
def view_doctor_detail():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("USE hospital")

    did = input("Enter Doctor ID: ").strip()
    cur.execute("SELECT * FROM doctors WHERE D_ID = %s", (did,))
    r = cur.fetchone()

    if not r:
        print("⚠️ Doctor not found.")
    else:
        print("\n=== Doctor Details ===")
        print(f"Doctor ID       : {r[0]}")
        print(f"Name             : {r[1]}")
        print(f"Specialization   : {r[2]}")
        print(f"Experience       : {r[3]} years")
        print(f"Fees             : ₹{r[4]:.2f}")
        print(f"Phone            : {r[5]}")
        print(f"Email            : {r[6]}")
        print(f"Gender           : {r[8]}")
        print(f"Address          : {r[9]}")
        print("Availability     :")
        try:
            avail = json.loads(r[7]) if r[7] else {}
            for day, slots in avail.items():
                print(f"  - {day}: {', '.join(slots)}")
        except Exception:
            print("  [Invalid JSON format]")
    cur.close()
    conn.close()


# ---------------------------------------------------------
# Edit doctor details
# ---------------------------------------------------------
def edit_doctor():
    """
    Edit details of an existing doctor.
    Allows updating a single field or multiple selected fields 
    instead of all details each time.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("USE hospital")

    did = input("Enter Doctor ID to edit: ").strip()
    cur.execute("SELECT * FROM doctors WHERE D_ID = %s", (did,))
    doc = cur.fetchone()

    if not doc:
        print("⚠️ Doctor not found.")
        cur.close()
        conn.close()
        return

    print(f"\nEditing Doctor: {doc[1]} ({doc[2]})")

    # Mapping field names with database columns
    fields = {
        "1": ("Name", doc[1]),
        "2": ("Specialization", doc[2]),
        "3": ("Experience", doc[3]),
        "4": ("Fees", doc[4]),
        "5": ("Phone_No", doc[5]),
        "6": ("Email", doc[6]),
        "7": ("Availability", doc[7]),
        "8": ("Gender", doc[8]),
        "9": ("Address", doc[9])
    }

    # Display editable fields
    print("\nSelect the field(s) to update:")
    for key, (field, value) in fields.items():
        display_val = value if value is not None else "NULL"
        print(f"{key}. {field} [{display_val}]")

    print("Enter field numbers separated by commas (e.g., 1,3,5):")
    choices = input("> ").replace(" ", "").split(",")

    updates = {}
    for choice in choices:
        if choice not in fields:
            print(f"⚠️ Invalid choice: {choice}")
            continue

        field, old_val = fields[choice]

        if field == "Availability":
            print("🕒 Editing Availability:")
            availability = {}
            while True:
                day = input("Enter day (blank to stop): ").strip()
                if not day:
                    break
                slots = input(f"Enter available time slots for {day} (comma-separated): ").split(",")
                availability[day] = [s.strip() for s in slots if s.strip()]
            updates[field] = json.dumps(availability)
        else:
            new_val = input(f"Enter new {field} (old: {old_val}): ").strip()
            if new_val:
                updates[field] = new_val

    if not updates:
        print("ℹ️ No updates made.")
        cur.close()
        conn.close()
        return

    # Build dynamic SQL query
    set_clause = ", ".join([f"{field} = %s" for field in updates])
    values = list(updates.values()) + [did]

    try:
        cur.execute(f"UPDATE doctors SET {set_clause} WHERE D_ID = %s", values)
        conn.commit()
        print("✅ Doctor details updated successfully.")
    except Exception as e:
        print("❌ Error updating doctor:", e)
    finally:
        cur.close()
        conn.close()



# ---------------------------------------------------------
# Delete doctor
# ---------------------------------------------------------
def delete_doctor():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("USE hospital")

    did = input("Enter Doctor ID to delete: ").strip()
    cur.execute("SELECT Name FROM doctors WHERE D_ID = %s", (did,))
    r = cur.fetchone()

    if not r:
        print("⚠️ Doctor not found.")
        return

    confirm = input(f"Are you sure you want to delete Dr. {r[0]} (Y/N)? ").strip().lower()
    if confirm == "y":
        try:
            cur.execute("DELETE FROM doctors WHERE D_ID = %s", (did,))
            conn.commit()
            print("✅ Doctor deleted successfully.")
        except Exception as e:
            print("❌ Error deleting doctor:", e)
    else:
        print("Deletion cancelled.")
    cur.close()
    conn.close()
