import sqlite3
from contextlib import closing

DB_NAME = "hospital_admin.db"


def get_connection() -> sqlite3.Connection:
    """
    Returns a SQLite connection with foreign key enforcement enabled.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """
    Create tables if they do not exist.
    This keeps schema creation in one place and makes the project portable.
    """
    with get_connection() as conn, closing(conn.cursor()) as cur:
        # Drop old tables to ensure a clean schema on each init (for demo purposes)
        cur.execute("DROP TABLE IF EXISTS invoice")
        cur.execute("DROP TABLE IF EXISTS treatment")
        cur.execute("DROP TABLE IF EXISTS room_assignment")
        cur.execute("DROP TABLE IF EXISTS appointment")
        cur.execute("DROP TABLE IF EXISTS patient")

        # Patients table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS patient (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                mrn             TEXT UNIQUE NOT NULL,   -- medical record number
                full_name       TEXT NOT NULL,
                date_of_birth   TEXT NOT NULL,          -- stored as ISO string YYYY-MM-DD
                sex             TEXT NOT NULL,
                phone           TEXT NOT NULL,
                email           TEXT,
                address         TEXT NOT NULL,
                primary_doctor  TEXT
            )
            """
        )

        # Appointments table, linked to patients
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS appointment (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id       INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,         -- YYYY-MM-DD
                appointment_time TEXT NOT NULL,         -- HH:MM
                doctor_name      TEXT NOT NULL,
                reason           TEXT,
                room             TEXT,
                FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
            )
            """
        )

        # Room assignments for inpatients
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS room_assignment (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id  INTEGER NOT NULL,
                room_number TEXT NOT NULL,
                room_type   TEXT,
                start_date  TEXT NOT NULL,   -- YYYY-MM-DD
                end_date    TEXT,            -- optional
                daily_rate  REAL NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
            )
            """
        )

        # Treatments or procedures
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS treatment (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id     INTEGER NOT NULL,
                treatment_date TEXT NOT NULL,   -- YYYY-MM-DD
                description    TEXT NOT NULL,
                cost           REAL NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
            )
            """
        )

        # Simple billing / invoice table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS invoice (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id   INTEGER NOT NULL,
                created_at   TEXT NOT NULL,  -- ISO timestamp
                total_amount REAL NOT NULL,
                status       TEXT NOT NULL DEFAULT 'OPEN', -- OPEN / PAID / CANCELLED
                notes        TEXT,
                FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
            )
            """
        )

        conn.commit()

        # Seed some demo data if database is empty
        cur.execute("SELECT COUNT(*) FROM patient")
        count_patients = cur.fetchone()[0] or 0
        if count_patients == 0:
            # Insert sample patients
            patients = [
                ("P001", "Emily Johnson", "1992-03-18", "F", "6175551010", "emily.johnson@example.com", "21 Green St, Boston, MA", "Dr. Smith"),
                ("P002", "Michael Brown", "1988-09-05", "M", "6175552020", "michael.brown@example.com", "14 Oak Ave, Cambridge, MA", "Dr. Brown"),
                ("P003", "Sophia Miller", "2000-12-22", "F", "6175553030", "sophia.miller@example.com", "9 River Rd, Somerville, MA", "Dr. Davis"),
            ]

            cur.executemany(
                """
                INSERT INTO patient (mrn, full_name, date_of_birth, sex, phone, email, address, primary_doctor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                patients,
            )

            # Load inserted patient ids
            cur.execute("SELECT id, mrn FROM patient")
            id_by_mrn = {mrn: pid for pid, mrn in cur.fetchall()}

            # Sample appointments
            appointments = [
                (id_by_mrn["P001"], "2025-01-10", "09:30", "Dr. Lee", "Follow-up", "101"),
                (id_by_mrn["P002"], "2025-01-11", "11:00", "Dr. Chen", "New patient", "202"),
                (id_by_mrn["P003"], "2025-01-12", "15:15", "Dr. Nguyen", "Routine check", "303"),
            ]
            cur.executemany(
                """
                INSERT INTO appointment (patient_id, appointment_date, appointment_time, doctor_name, reason, room)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                appointments,
            )

            # Sample room assignments
            room_assignments = [
                (id_by_mrn["P001"], "A101", "Private", "2025-01-09", None, 350.0),
                (id_by_mrn["P002"], "B210", "General", "2025-01-10", "2025-01-12", 180.0),
            ]
            cur.executemany(
                """
                INSERT INTO room_assignment (patient_id, room_number, room_type, start_date, end_date, daily_rate)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                room_assignments,
            )

            # Sample treatments
            treatments = [
                (id_by_mrn["P001"], "2025-01-10", "MRI Scan", 500.0),
                (id_by_mrn["P001"], "2025-01-10", "Consultation", 120.0),
                (id_by_mrn["P002"], "2025-01-11", "Blood test", 80.0),
            ]
            cur.executemany(
                """
                INSERT INTO treatment (patient_id, treatment_date, description, cost)
                VALUES (?, ?, ?, ?)
                """,
                treatments,
            )

            # Sample invoices
            invoices = [
                (id_by_mrn["P001"], "2025-01-10T16:30:00", 970.0, "OPEN", "Includes scan and consultation"),
                (id_by_mrn["P002"], "2025-01-11T13:00:00", 260.0, "PAID", "Two days stay + lab work"),
            ]
            cur.executemany(
                """
                INSERT INTO invoice (patient_id, created_at, total_amount, status, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                invoices,
            )

        conn.commit()
