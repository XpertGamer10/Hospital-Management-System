# main.py

from db_setup import init_database
from patient_ops import (
    register_patient,
    view_my_appointments,
    print_receipt_by_appointment,
    delete_patient
)
from appointment_ops import book_appointment
from admin_ops import admin_menu, forgot_credentials


def patient_portal_menu():
    """Patient-side menu and operations."""
    while True:
        print("\n--- 🧍 PATIENT PORTAL ---")
        print("1. Register as New Patient")
        print("2. Book Appointment")
        print("3. View My Appointments (by ID or Phone)")
        print("4. Print My Receipt (by Appointment ID)")
        print("5. Delete My Account")
        print("6. Back to Main Menu")

        ch = input("Choose an option: ").strip()

        if ch == '1':
            register_patient()
        elif ch == '2':
            book_appointment()
        elif ch == '3':
            view_my_appointments()
        elif ch == '4':
            print_receipt_by_appointment()
        elif ch == '5':
            delete_patient()
        elif ch == '6':
            break
        else:
            print("⚠️ Invalid choice. Please try again.")


def main():
    """Main entry point for Hospital Management System."""
    init_database()
    print("\n🏥 Welcome to Hospital Management System 🏥\n")

    while True:
        print("=== MAIN MENU ===")
        print("1. Patient Portal")
        print("2. Admin Portal (Login Required)")
        print("3. Forgot Username/Password (Admin Only)")
        print("4. Exit\n")

        choice = input("Choose: ").strip()

        if choice == '1':
            patient_portal_menu()
        elif choice == '2':
            admin_menu()  # Full admin system with doctor/certificate/receipt controls
        elif choice == '3':
            forgot_credentials()
        elif choice == '4':
            print("👋 Thank you for using the Hospital Management System. Stay healthy!")
            break
        else:
            print("⚠️ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
