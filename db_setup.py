# db_setup.py
import mysql.connector as connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysql@123",
    "database": "hospital"
}

def init_database():
    """
    Create database (if not exists) and required tables.
    Safe to run multiple times.
    """
    tmp_conn = None
    tmp_cur = None
    try:
        # Connect without database to ensure DB exists
        tmp_conn = connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        tmp_cur = tmp_conn.cursor()
        tmp_cur.execute("CREATE DATABASE IF NOT EXISTS hospital;")
        tmp_cur.execute("USE hospital;")

        # ----------------------------------------------------------------
        # Admin table (secure login storage)
        tmp_cur.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            Admin_ID INT AUTO_INCREMENT PRIMARY KEY,
            Username VARCHAR(50) UNIQUE NOT NULL,
            Password VARCHAR(255) NOT NULL,
            Email VARCHAR(100),
            Full_Name VARCHAR(100),
            Created_On DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Ensure a default admin exists
        tmp_cur.execute("SELECT COUNT(*) FROM admin;")
        if tmp_cur.fetchone()[0] == 0:
            tmp_cur.execute("""
                INSERT INTO admin (Username, Password, Email, Full_Name)
                VALUES ('admin', 'admin123', 'admin@hospital.com', 'System Administrator');
            """)

        # ----------------------------------------------------------------
        # patients
        tmp_cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            P_ID INT PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(50) NOT NULL,
            Age INT CHECK (Age > 0),
            Gender ENUM('Male', 'Female', 'Other'),
            Phone_No VARCHAR(13) UNIQUE,
            Email VARCHAR(50) UNIQUE,
            Address VARCHAR(100),
            Date_Registered DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # doctors
        tmp_cur.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            D_ID INT PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(50) NOT NULL,
            Specialization VARCHAR(50),
            Experience INT,
            Fees DECIMAL(10,2),
            Phone_No VARCHAR(13) UNIQUE,
            Email VARCHAR(50) UNIQUE,
            Availability JSON,
            Gender ENUM('Male', 'Female', 'Other'),
            Address VARCHAR(100)
        );
        """)

        # appointments
        tmp_cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            A_ID INT PRIMARY KEY AUTO_INCREMENT,
            P_ID INT,
            D_ID INT,
            Appointment_Date DATE,
            Time_Slot VARCHAR(50),
            Reason VARCHAR(200),
            Status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
            Date_Created DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (P_ID) REFERENCES patients(P_ID) ON DELETE CASCADE,
            FOREIGN KEY (D_ID) REFERENCES doctors(D_ID) ON DELETE CASCADE
        );
        """)

        # billing
        tmp_cur.execute("""
        CREATE TABLE IF NOT EXISTS billing (
            Bill_ID INT AUTO_INCREMENT PRIMARY KEY,
            A_ID INT,
            Amount DECIMAL(10,2),
            Payment_Mode ENUM('Cash','Card','UPI'),
            Date_Paid DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (A_ID) REFERENCES appointments(A_ID) ON DELETE SET NULL
        );
        """)

        # receipts (human-readable bills)
        tmp_cur.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            Receipt_ID INT AUTO_INCREMENT PRIMARY KEY,
            A_ID INT NULL,
            P_ID INT NOT NULL,
            Bill_No VARCHAR(50) UNIQUE NOT NULL,
            Amount DECIMAL(10,2) NOT NULL,
            Payment_Mode ENUM('Cash','Card','UPI') DEFAULT 'Cash',
            Date_Paid DATETIME DEFAULT CURRENT_TIMESTAMP,
            Notes VARCHAR(255),
            FOREIGN KEY (A_ID) REFERENCES appointments(A_ID),
            FOREIGN KEY (P_ID) REFERENCES patients(P_ID)
        );
        """)

        # beds (inventory)
        tmp_cur.execute("""
        CREATE TABLE IF NOT EXISTS beds (
            Bed_ID INT AUTO_INCREMENT PRIMARY KEY,
            Department VARCHAR(50) NOT NULL,
            Bed_No VARCHAR(20) NOT NULL,
            Is_Occupied TINYINT(1) DEFAULT 0,
            Current_P_ID INT NULL,
            UNIQUE (Department, Bed_No),
            FOREIGN KEY (Current_P_ID) REFERENCES patients(P_ID)
        );
        """)

        # Populate default beds if empty
        tmp_cur.execute("SELECT COUNT(*) FROM beds")
        if tmp_cur.fetchone()[0] == 0:
            departments = {
                "OPD": 10,
                "IPD": 30,
                "ICU": 6,
                "Emergency": 8,
                "Radiology": 4,
                "Surgery": 12
            }
            for dept, cnt in departments.items():
                for i in range(1, cnt+1):
                    bed_no = f"{dept[:3].upper()}-{i:02d}"
                    tmp_cur.execute("INSERT INTO beds (Department, Bed_No) VALUES (%s, %s)", (dept, bed_no))

        # admissions (track patients)
        tmp_cur.execute("""
        CREATE TABLE IF NOT EXISTS admissions (
            Admission_ID INT AUTO_INCREMENT PRIMARY KEY,
            P_ID INT NOT NULL,
            Bed_ID INT NOT NULL,
            Department VARCHAR(50) NOT NULL,
            Admit_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
            Discharge_Date DATETIME NULL,
            Status ENUM('Admitted','Discharged') DEFAULT 'Admitted',
            Notes VARCHAR(255),
            FOREIGN KEY (P_ID) REFERENCES patients(P_ID),
            FOREIGN KEY (Bed_ID) REFERENCES beds(Bed_ID)
        );
        """)

        # certificates (birth/death)
        tmp_cur.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            Certificate_ID INT AUTO_INCREMENT PRIMARY KEY,
            P_ID INT NULL,
            Type ENUM('Birth','Death') NOT NULL,
            Name VARCHAR(100) NOT NULL,
            DOB DATE NULL,
            DOD DATE NULL,
            Parent_Guardian VARCHAR(100),
            Place_Of_Event VARCHAR(100),
            Notes TEXT,
            Issued_By VARCHAR(100) DEFAULT 'Hospital Admin',
            Date_Issued DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (P_ID) REFERENCES patients(P_ID) ON DELETE SET NULL
        );
        """)

        tmp_conn.commit()
        print("✅ Database and tables checked/created successfully.")

    except connector.Error as e:
        print("❌ DB setup error:", e)

    finally:
        try:
            if tmp_cur:
                tmp_cur.close()
            if tmp_conn:
                tmp_conn.close()
        except:
            pass


def get_connection():
    """Returns a new connection using the `hospital` database."""
    return connector.connect(**DB_CONFIG)
