import json
from datetime import datetime
from tabulate import tabulate
from db_setup import get_connection
from Utils.utils import display_table, build_receipt_text, save_receipt_text


def book_appointment():
    """
    Patient books their appointment.
    - Validates date against doctor's available days.
    - Shows full doctor details with availability.
    - Auto-handles billing & receipt.
    - Privacy preserved: patients see only doctor info, not others.
    """
    print("\n--- Book Appointment ---")
    pid_input = input("Enter your Patient ID (or press Enter to use phone): ").strip()
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("USE hospital")

        # --- Identify Patient ---
        if not pid_input:
            phone = input("Enter your registered Phone Number: ").strip()
            cur.execute("SELECT P_ID, Name FROM patients WHERE Phone_No = %s", (phone,))
            p = cur.fetchone()
            if not p:
                print("⚠️ No patient found with that phone number.")
                return
            pid = p[0]
            print(f"👋 Welcome back, {p[1]}!")
        else:
            cur.execute("SELECT Name FROM patients WHERE P_ID = %s", (pid_input,))
            p = cur.fetchone()
            if not p:
                print("⚠️ No patient found with that ID.")
                return
            pid = pid_input
            print(f"👋 Welcome back, {p[0]}!")

        # --- Show Doctors ---
        cur.execute("""
            SELECT D_ID, Name, Specialization, Experience, Fees, Gender, Availability 
            FROM doctors
        """)
        doctors = cur.fetchall()

        if not doctors:
            print("⚠️ No doctors are available at the moment.")
            return

        display_data = []
        for d in doctors:
            availability = json.loads(d[6]) if d[6] else {}
            available_days = ", ".join(availability.keys()) if availability else "Not Set"
            display_data.append([
                d[0], d[1], d[2], f"{d[3]} yrs", f"₹{d[4]:.2f}", d[5], available_days
            ])
        print(tabulate(display_data, headers=[
            "D_ID", "Doctor Name", "Specialization", "Experience", "Fees", "Gender", "Available Days"
        ], tablefmt="grid"))

        did = input("\nEnter Doctor ID: ").strip()

        # --- Verify doctor exists ---
        cur.execute("SELECT Availability FROM doctors WHERE D_ID = %s", (did,))
        res = cur.fetchone()
        if not res:
            print("⚠️ Doctor not found.")
            return

        availability = json.loads(res[0]) if res[0] else {}
        if availability:
            print("\nDoctor Availability:")
            for day, slots in availability.items():
                print(f"  {day}: {', '.join(slots)}")
        else:
            print("⚠️ Availability not set for this doctor.")

        # --- Date Validation + Day Check ---
        while True:
            appointment_date = input("\nEnter appointment date (YYYY-MM-DD): ").strip()
            try:
                appt_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
                if appt_date < datetime.now().date():
                    print("❌ Date cannot be in the past.")
                    continue

                day_name = appt_date.strftime("%A")
                if day_name not in availability.keys():
                    print(f"❌ The doctor is not available on {day_name}.")
                    print(f"🗓️ Available days: {', '.join(availability.keys())}")
                    continue

                break
            except ValueError:
                print("❌ Invalid date format. Use YYYY-MM-DD.")

        # --- Time Slot Validation ---
        print("\nAvailable time slots for that day:")
        for i, slot in enumerate(availability[day_name], start=1):
            print(f"{i}. {slot}")
        slot_choice = input("Choose time slot number: ").strip()
        try:
            slot_choice = int(slot_choice)
            time_slot = availability[day_name][slot_choice - 1]
        except (ValueError, IndexError):
            print("⚠️ Invalid slot selection.")
            return

        reason = input("Enter reason for appointment: ").strip()

        # --- Insert Appointment ---
        cur.execute("""
            INSERT INTO appointments (P_ID, D_ID, Appointment_Date, Time_Slot, Reason)
            VALUES (%s, %s, %s, %s, %s)
        """, (pid, did, appt_date, time_slot, reason))
        conn.commit()
        aid = cur.lastrowid
        print(f"\n✅ Appointment booked successfully (A_ID = {aid})")

        # --- Optional Payment ---
        pay_now = input("Pay consultation fees now? (y/n): ").strip().lower()
        if pay_now == 'y':
            cur.execute("SELECT Fees FROM doctors WHERE D_ID = %s", (did,))
            fee_row = cur.fetchone()
            fee_amount = float(fee_row[0]) if fee_row else 0.0
            mode = input("Payment mode (Cash/Card/UPI): ").strip().capitalize()
            cur.execute("""
                INSERT INTO billing (A_ID, Amount, Payment_Mode) 
                VALUES (%s, %s, %s)
            """, (aid, fee_amount, mode))
            conn.commit()
            print(f"✅ Payment recorded — Amount: ₹{fee_amount:.2f}")

        # --- Generate Receipt ---
        cur.execute("SELECT * FROM appointments WHERE A_ID = %s", (aid,))
        appointment = cur.fetchone()
        cur.execute("SELECT * FROM patients WHERE P_ID = %s", (appointment[1],))
        patient = cur.fetchone()
        cur.execute("SELECT * FROM doctors WHERE D_ID = %s", (appointment[2],))
        doctor = cur.fetchone()
        cur.execute("""
            SELECT Amount FROM billing WHERE A_ID = %s 
            ORDER BY Date_Paid DESC LIMIT 1
        """, (aid,))
        bill = cur.fetchone()
        bill_amount = bill[0] if bill else None

        text = build_receipt_text(patient, doctor, appointment, bill_amount)
        print("\n" + text + "\n")
        fname = f"receipt_A{aid}_P{patient[0]}.txt"
        path = save_receipt_text(fname, text)
        print(f"🧾 Receipt saved at: {path}")

    except Exception as e:
        print("❌ Error booking appointment:", e)

    finally:
        cur.close()
        conn.close()


def view_all_appointments():
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("USE hospital")
        cur.execute("""
            SELECT a.A_ID, p.Name, d.Name, d.Specialization, a.Appointment_Date, a.Time_Slot, a.Reason, a.Status
            FROM appointments a
            JOIN patients p ON a.P_ID = p.P_ID
            JOIN doctors d ON a.D_ID = d.D_ID
            ORDER BY a.Appointment_Date, a.Time_Slot
        """)
        rows = cur.fetchall()
        if not rows:
            print("No appointments found.")
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

def view_appointments_datewise():
    date = input("Enter date to search (YYYY-MM-DD): ").strip()
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("USE hospital")
        cur.execute("""
            SELECT a.A_ID, p.Name, d.Name, d.Specialization, a.Time_Slot, a.Reason, a.Status
            FROM appointments a
            JOIN patients p ON a.P_ID = p.P_ID
            JOIN doctors d ON a.D_ID = d.D_ID
            WHERE a.Appointment_Date = %s
            ORDER BY a.Time_Slot
        """, (date,))
        rows = cur.fetchall()
        if not rows:
            print("No appointments found for that date.")
            return
        for r in rows:
            print("\n📌 Appointment")
            print(f"Appointment ID : {r[0]}")
            print(f"Patient Name   : {r[1]}")
            print(f"Doctor         : Dr. {r[2]} ({r[3]})")
            print(f"Time           : {r[4]}")
            print(f"Reason         : {r[5]}")
            print(f"Status         : {r[6]}")
            print("-" * 50)
    except Exception as e:
        print("❌ Error:", e)
    finally:
        cur.close(); conn.close()

def edit_appointment():
    aid = input("Enter Appointment ID to edit: ").strip()
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("USE hospital")
        cur.execute("SELECT * FROM appointments WHERE A_ID = %s", (aid,))
        a = cur.fetchone()
        if not a:
            print("⚠️ Appointment not found.")
            return
        print("Press Enter to keep existing value.")
        date = input(f"Appointment Date [{a[3]}]: ").strip() or a[3]
        time_slot = input(f"Time Slot [{a[4]}]: ").strip() or a[4]
        reason = input(f"Reason [{a[5]}]: ").strip() or a[5]
        status = input(f"Status (Scheduled/Completed/Cancelled) [{a[6]}]: ").strip().capitalize() or a[6]
        cur.execute("""
            UPDATE appointments SET Appointment_Date=%s, Time_Slot=%s, Reason=%s, Status=%s WHERE A_ID=%s
        """, (date, time_slot, reason, status, aid))
        conn.commit()
        print("✅ Appointment updated.")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        cur.close(); conn.close()

def delete_appointment():
    aid = input("Enter Appointment ID to delete: ").strip()
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("USE hospital")
        cur.execute("DELETE FROM appointments WHERE A_ID = %s", (aid,))
        conn.commit()
        print("✅ Appointment deleted (if existed).")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        cur.close(); conn.close()

def record_payment():
    aid = input("Enter Appointment ID to record payment for: ").strip()
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("USE hospital")
        # fetch appointment & doctor fee
        cur.execute("SELECT D_ID FROM appointments WHERE A_ID = %s", (aid,))
        row = cur.fetchone()
        if not row:
            print("⚠️ Appointment not found.")
            return
        d_id = row[0]
        cur.execute("SELECT Fees FROM doctors WHERE D_ID = %s", (d_id,))
        fee = cur.fetchone()
        amount = float(fee[0]) if fee and fee[0] else float(input("Enter amount: ").strip())
        mode = input("Payment Mode (Cash/Card/UPI): ").strip().capitalize()
        cur.execute("INSERT INTO billing (A_ID, Amount, Payment_Mode) VALUES (%s,%s,%s)", (aid, amount, mode))
        conn.commit()
        print(f"✅ Payment recorded: ₹{amount:.2f}")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        cur.close(); conn.close()
