import sqlite3
import datetime
from pathlib import Path

DB_PATH = Path(__file__).with_name("hospital_admin.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        PRAGMA foreign_keys = OFF;
        DROP TABLE IF EXISTS invoice;
        DROP TABLE IF EXISTS treatment;
        DROP TABLE IF EXISTS room_assignment;
        DROP TABLE IF EXISTS appointment;
        DROP TABLE IF EXISTS patient;
        PRAGMA foreign_keys = ON;
        """
    )

    cur.executescript(
        """
        CREATE TABLE patient (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            mrn             TEXT NOT NULL UNIQUE,
            full_name       TEXT NOT NULL,
            date_of_birth   TEXT NOT NULL,
            sex             TEXT NOT NULL CHECK (sex IN ('M', 'F', 'O')),
            phone           TEXT NOT NULL,
            email           TEXT,
            address         TEXT,
            primary_doctor  TEXT,
            created_at      TEXT NOT NULL
        );

        CREATE TABLE appointment (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id       INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            doctor_name      TEXT NOT NULL,
            reason           TEXT,
            room             TEXT,
            status           TEXT NOT NULL CHECK (status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED', 'NO_SHOW')),
            department       TEXT,
            created_at       TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
        );

        CREATE TABLE room_assignment (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  INTEGER NOT NULL,
            room_number TEXT NOT NULL,
            room_type   TEXT,
            start_date  TEXT NOT NULL,
            end_date    TEXT,
            daily_rate  REAL NOT NULL CHECK (daily_rate >= 0),
            created_at  TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
        );

        CREATE TABLE treatment (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id     INTEGER NOT NULL,
            treatment_date TEXT NOT NULL,
            description    TEXT NOT NULL,
            cost           REAL NOT NULL CHECK (cost >= 0),
            created_at     TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
        );

        CREATE TABLE invoice (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id   INTEGER NOT NULL,
            created_at   TEXT NOT NULL,
            total_amount REAL NOT NULL CHECK (total_amount >= 0),
            status       TEXT NOT NULL CHECK (status IN ('OPEN', 'PAID', 'CANCELLED')),
            notes        TEXT,
            FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
        );

        CREATE INDEX idx_appt_date ON appointment(appointment_date);
        CREATE INDEX idx_appt_doctor ON appointment(doctor_name);
        CREATE INDEX idx_invoice_status ON invoice(status);
        """
    )

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    patients = [
        ("P1001", "Emily Johnson", "1990-03-12", "F", "6175550101", "emily.johnson@example.com", "Boston, MA", "Dr. Carter"),
        ("P1002", "Michael Smith", "1985-07-25", "M", "6175550102", "michael.smith@example.com", "Cambridge, MA", "Dr. Carter"),
        ("P1003", "Olivia Brown", "1992-09-05", "F", "6175550103", "olivia.brown@example.com", "Somerville, MA", "Dr. Patel"),
        ("P1004", "Ethan Davis", "1978-01-18", "M", "6175550104", "ethan.davis@example.com", "Brookline, MA", "Dr. Patel"),
        ("P1005", "Sophia Wilson", "1995-11-30", "F", "6175550105", "sophia.wilson@example.com", "Boston, MA", "Dr. Lee"),
        ("P1006", "Liam Anderson", "1988-04-07", "M", "6175550106", "liam.anderson@example.com", "Quincy, MA", "Dr. Lee"),
        ("P1007", "Ava Martinez", "2000-06-22", "F", "6175550107", "ava.martinez@example.com", "Boston, MA", "Dr. Ramirez"),
        ("P1008", "Noah Taylor", "1993-02-14", "M", "6175550108", "noah.taylor@example.com", "Medford, MA", "Dr. Ramirez"),
        ("P1009", "Isabella Thomas", "1989-12-03", "F", "6175550109", "isabella.thomas@example.com", "Boston, MA", "Dr. Carter"),
        ("P1010", "James White", "1975-05-19", "M", "6175550110", "james.white@example.com", "Cambridge, MA", "Dr. Lee"),
        ("P1011", "Mia Harris", "1998-08-09", "F", "6175550111", "mia.harris@example.com", "Boston, MA", "Dr. Patel"),
        ("P1012", "Alexander Clark", "1983-10-28", "M", "6175550112", "alex.clark@example.com", "Brookline, MA", "Dr. Carter"),
        ("P1013", "Charlotte Lewis", "1991-01-03", "F", "6175550113", "charlotte.lewis@example.com", "Somerville, MA", "Dr. Lee"),
        ("P1014", "Benjamin Walker", "1987-09-17", "M", "6175550114", "benjamin.walker@example.com", "Boston, MA", "Dr. Ramirez"),
        ("P1015", "Amelia Hall", "1994-12-21", "F", "6175550115", "amelia.hall@example.com", "Cambridge, MA", "Dr. Patel"),
    ]

    cur.executemany(
        """
        INSERT INTO patient (mrn, full_name, date_of_birth, sex, phone, email, address, primary_doctor, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [(*p, now) for p in patients],
    )


    cur.execute("SELECT id, mrn FROM patient")
    id_by_mrn = {mrn: pid for pid, mrn in cur.fetchall()}

    appointments = [
        ("P1001", "2025-10-01", "09:00", "Dr. Carter", "Annual physical", "101A", "SCHEDULED", "Primary Care"),
        ("P1002", "2025-10-01", "09:30", "Dr. Carter", "Follow up visit", "101B", "COMPLETED", "Primary Care"),
        ("P1003", "2025-10-02", "10:00", "Dr. Patel", "Chest pain", "202", "SCHEDULED", "Cardiology"),
        ("P1004", "2025-10-02", "11:00", "Dr. Patel", "Blood pressure check", "203", "COMPLETED", "Cardiology"),
        ("P1005", "2025-10-03", "09:15", "Dr. Lee", "Migraine", "305", "SCHEDULED", "Neurology"),
        ("P1006", "2025-10-03", "10:45", "Dr. Lee", "Dizziness", "305", "CANCELLED", "Neurology"),
        ("P1007", "2025-10-04", "14:00", "Dr. Ramirez", "Asthma review", "410", "SCHEDULED", "Pulmonology"),
        ("P1008", "2025-10-04", "14:30", "Dr. Ramirez", "Cough and fever", "410", "NO_SHOW", "Pulmonology"),
        ("P1009", "2025-10-05", "15:00", "Dr. Carter", "Diabetes follow up", "102", "SCHEDULED", "Endocrinology"),
        ("P1010", "2025-10-05", "15:30", "Dr. Lee", "Back pain", "306", "COMPLETED", "Orthopedics"),
        ("P1011", "2025-09-28", "13:00", "Dr. Patel", "Palpitations", "204", "COMPLETED", "Cardiology"),
        ("P1012", "2025-09-29", "11:30", "Dr. Carter", "Lab review", "103", "COMPLETED", "Primary Care"),
        ("P1013", "2025-09-30", "10:15", "Dr. Lee", "Headache", "307", "SCHEDULED", "Neurology"),
        ("P1014", "2025-09-30", "16:00", "Dr. Ramirez", "Shortness of breath", "411", "SCHEDULED", "Pulmonology"),
        ("P1015", "2025-10-06", "09:45", "Dr. Patel", "Chest discomfort", "205", "SCHEDULED", "Cardiology"),
    ]

    cur.executemany(
        """
        INSERT INTO appointment
            (patient_id, appointment_date, appointment_time, doctor_name, reason, room, status, department, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                id_by_mrn[mrn],
                date,
                time,
                doctor,
                reason,
                room,
                status,
                dept,
                now,
            )
            for (mrn, date, time, doctor, reason, room, status, dept) in appointments
        ],
    )

    room_assignments = [
        ("P1003", "2025-10-02", "2025-10-05", "202", "Cardiology Ward", 650.0),
        ("P1004", "2025-10-02", None, "203", "Cardiology Ward", 650.0),
        ("P1007", "2025-10-04", None, "410", "Pulmonology Ward", 550.0),
        ("P1014", "2025-09-30", None, "411", "Pulmonology Ward", 550.0),
    ]

    cur.executemany(
        """
        INSERT INTO room_assignment
            (patient_id, room_number, room_type, start_date, end_date, daily_rate, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                id_by_mrn[mrn],
                room,
                rtype,
                start,
                end,
                rate,
                now,
            )
            for (mrn, start, end, room, rtype, rate) in room_assignments
        ],
    )

    treatments = [
        ("P1003", "2025-10-02", "ECG and cardiac enzymes", 400.0),
        ("P1003", "2025-10-03", "Echocardiogram", 600.0),
        ("P1004", "2025-10-02", "Blood pressure stabilization", 250.0),
        ("P1007", "2025-10-04", "Nebulizer therapy", 180.0),
        ("P1008", "2025-10-04", "Initial respiratory assessment", 200.0),
        ("P1010", "2025-10-05", "Lumbar X ray", 350.0),
        ("P1011", "2025-09-28", "Holter monitor", 500.0),
    ]

    cur.executemany(
        """
        INSERT INTO treatment
            (patient_id, treatment_date, description, cost, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                id_by_mrn[mrn],
                tdate,
                desc,
                cost,
                now,
            )
            for (mrn, tdate, desc, cost) in treatments
        ],
    )

    invoices = [
        ("P1003", "2025-10-05 10:00", 1650.0, "OPEN", "Inpatient stay and diagnostics"),
        ("P1004", "2025-10-03 09:30", 900.0, "PAID", "Monitoring and medication"),
        ("P1007", "2025-10-04 18:00", 430.0, "OPEN", "Asthma treatment"),
        ("P1008", "2025-10-04 18:30", 200.0, "CANCELLED", "No show"),
        ("P1010", "2025-10-05 17:00", 350.0, "PAID", "Outpatient imaging"),
        ("P1011", "2025-09-29 08:30", 500.0, "PAID", "Cardiac monitoring"),
    ]

    cur.executemany(
        """
        INSERT INTO invoice
            (patient_id, created_at, total_amount, status, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                id_by_mrn[mrn],
                created,
                amount,
                status,
                notes,
            )
            for (mrn, created, amount, status, notes) in invoices
        ],
    )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
