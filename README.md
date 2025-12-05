# Hospital Admin Desktop App

This project is a small desktop application for managing basic hospital data:

- A **patient registry** (demographics and contact information)
- **Appointments** linked to patients
- **Room assignments** for inpatients
- **Treatments / procedures** with per‑patient cost tracking
- **Billing / invoices** recorded per patient

It is implemented in:

- Python 3
- Tkinter for the graphical user interface
- SQLite for the relational database

The goal is to demonstrate a simple, self‑contained CRUD application that uses a normalized schema and enforces referential integrity.

## Features

### Patients

- Create, edit, and delete patients
- Fields:
  - Medical record number (MRN)
  - Full name
  - Date of birth
  - Sex
  - Phone
  - Email (optional)
  - Address
  - Primary doctor (text field)
- Input validation for required fields, date format, and phone number

### Appointments

- Create appointments bound to an existing patient
- Fields:
  - Patient (chosen from a dropdown)
  - Date
  - Time
  - Doctor name
  - Reason (optional)
  - Room (optional)
- Appointments are stored in a separate table with a foreign key to the patient table.

If a patient is deleted, their appointments are automatically removed because of the `ON DELETE CASCADE` foreign key constraint.

### Room assignments

- Assign a patient to a room with:
  - Room number
  - Room type (for example: ICU, General, Private)
  - Start and end date
  - Daily rate
- Each assignment references the patient through a foreign key.

### Treatments

- Record treatments or procedures performed for a patient
- Fields:
  - Date
  - Description
  - Cost
- These records can later be used for reporting or billing.

### Billing / Invoices

- Create simple invoices for patients
- Fields:
  - Patient
  - Total amount
  - Status (OPEN, PAID, CANCELLED)
  - Notes
- Invoices are stored in a dedicated `invoice` table.


- Create appointments bound to an existing patient
- Fields:
  - Patient (chosen from a dropdown)
  - Date
  - Time
  - Doctor name
  - Reason (optional)
  - Room (optional)
- Appointments are stored in a separate table with a foreign key to the patient table.

If a patient is deleted, their appointments are automatically removed because of the `ON DELETE CASCADE` foreign key constraint.

## Database design

The application stores data in a local SQLite database file named `hospital_admin.db`.

Tables:

```sql
CREATE TABLE patient (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    mrn             TEXT UNIQUE NOT NULL,
    full_name       TEXT NOT NULL,
    date_of_birth   TEXT NOT NULL,   -- stored as YYYY-MM-DD
    sex             TEXT NOT NULL,
    phone           TEXT NOT NULL,
    email           TEXT,
    address         TEXT NOT NULL,
    primary_doctor  TEXT
);

CREATE TABLE appointment (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER NOT NULL,
    appointment_date TEXT NOT NULL,  -- YYYY-MM-DD
    appointment_time TEXT NOT NULL,  -- HH:MM
    doctor_name      TEXT NOT NULL,
    reason           TEXT,
    room             TEXT,
    FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
);

CREATE TABLE room_assignment (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id  INTEGER NOT NULL,
    room_number TEXT NOT NULL,
    room_type   TEXT,
    start_date  TEXT NOT NULL,
    end_date    TEXT,
    daily_rate  REAL NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
);

CREATE TABLE treatment (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id     INTEGER NOT NULL,
    treatment_date TEXT NOT NULL,
    description    TEXT NOT NULL,
    cost           REAL NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
);

CREATE TABLE invoice (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id   INTEGER NOT NULL,
    created_at   TEXT NOT NULL,
    total_amount REAL NOT NULL,
    status       TEXT NOT NULL DEFAULT 'OPEN',
    notes        TEXT,
    FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
);
``````

Foreign key enforcement is enabled by running `PRAGMA foreign_keys = ON` for each connection.

## Running the application

1. Install Python 3.
2. Install any optional dependencies (Tkinter is included with most standard Python distributions on Windows/macOS):

   ```bash
   pip install -r requirements.txt
   ```

3. Run the main script:

   ```bash
   python main.py
   ```

4. Log in using the default admin credentials:

   - **Username:** `admin`
   - **Password:** `admin`

From the dashboard you can open:

- **Patient Registry** – to manage patients
- **Appointments** – to schedule and review appointments

The database file (`hospital_admin.db`) is created automatically on first launch if it does not exist.

## Notes and possible extensions

This project is intentionally small and focused. Natural extensions would be:

- A proper user table and login system with hashed passwords
- Separate roles for reception staff vs. doctors
- Additional tables for billing, treatments, or rooms
- More advanced reports, such as number of appointments per doctor per week or patient visit frequency by month
