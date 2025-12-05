import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from db import get_connection


class AppointmentWindow(tk.Toplevel):
    """
    Window to create and view appointments.

    Each appointment is linked to an existing patient.
    """

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Appointments")
        self.geometry("1100x650")
        self.configure(bg="#f4fbff")

        self.patient_id_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.doctor_var = tk.StringVar()
        self.reason_var = tk.StringVar()
        self.room_var = tk.StringVar()

        self.search_var = tk.StringVar()
        self.selected_appointment_id: int | None = None

        self._patients_map: dict[str, int] = {}  # "MRN - Name" -> patient_id

        self._build_ui()
        self._load_patients()
        self._load_appointments()

    def _build_ui(self) -> None:
        header = ttk.Label(self, text="Appointments", font=("Segoe UI", 18, "bold"))
        header.pack(pady=(10, 5))

        main = ttk.Frame(self, padding=10)
        main.pack(expand=True, fill="both")

        form = ttk.LabelFrame(main, text="New appointment", padding=10)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # patient dropdown
        ttk.Label(form, text="Patient").grid(row=0, column=0, sticky="w", pady=3)
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_id_var, state="readonly", width=35)
        self.patient_combo.grid(row=0, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.date_var).grid(row=1, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Time (HH:MM)").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.time_var).grid(row=2, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Doctor").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.doctor_var).grid(row=3, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Reason").grid(row=4, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.reason_var).grid(row=4, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Room").grid(row=5, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.room_var).grid(row=5, column=1, sticky="ew", pady=3)

        form.columnconfigure(1, weight=1)

        button_bar = ttk.Frame(form)
        button_bar.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(button_bar, text="New", command=self._on_new).grid(row=0, column=0, padx=5)
        ttk.Button(button_bar, text="Save", command=self._on_save).grid(row=0, column=1, padx=5)
        ttk.Button(button_bar, text="Delete", command=self._on_delete).grid(row=0, column=2, padx=5)

        # table + search
        table_frame = ttk.LabelFrame(main, text="Appointments", padding=10)
        table_frame.grid(row=0, column=1, sticky="nsew")

        search_row = ttk.Frame(table_frame)
        search_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(search_row, text="Search (patient / doctor / date):").pack(side="left")
        search_entry = ttk.Entry(search_row, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=5)
        ttk.Button(search_row, text="Go", command=self._on_search).pack(side="left")
        ttk.Button(search_row, text="Clear", command=self._on_clear_search).pack(side="left", padx=(5, 0))

        columns = ("id", "patient", "date", "time", "doctor", "room")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        headings = {
            "id": "ID",
            "patient": "Patient",
            "date": "Date",
            "time": "Time",
            "doctor": "Doctor",
            "room": "Room",
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100 if col not in ("patient", "doctor") else 150, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self._on_select_row)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")

        table_frame.rowconfigure(1, weight=1)
        table_frame.columnconfigure(0, weight=1)

        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

    # ------------------------------------------------------------------ loading data

    def _load_patients(self) -> None:
        self._patients_map.clear()
        options: list[str] = []
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, mrn, full_name FROM patient ORDER BY full_name")
            for patient_id, mrn, name in cur.fetchall():
                label = f"{mrn} - {name}"
                self._patients_map[label] = patient_id
                options.append(label)

        self.patient_combo["values"] = options
        if options:
            self.patient_combo.current(0)

    def _load_appointments(self, search: str | None = None) -> None:
        self.tree.delete(*self.tree.get_children())
        with get_connection() as conn:
            cur = conn.cursor()
            base_sql = (
                "SELECT a.id, p.full_name, a.appointment_date, a.appointment_time, a.doctor_name, a.room "
                "FROM appointment a JOIN patient p ON a.patient_id = p.id"
            )
            params: tuple = ()
            if search:
                like = f"%{search.strip()}%"
                base_sql += (
                    " WHERE p.full_name LIKE ? OR a.doctor_name LIKE ? OR a.appointment_date LIKE ?"
                )
                params = (like, like, like)
            base_sql += " ORDER BY a.appointment_date, a.appointment_time"
            cur.execute(base_sql, params)
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)

    # ------------------------------------------------------------------ actions


    # ------------------------------ actions

    def _on_new(self) -> None:
        """Reset the form to create a new appointment."""
        self.selected_appointment_id = None
        self._clear_form()

    def _on_save(self) -> None:
        """Create a new appointment or update the selected one."""
        if not self._validate_form():
            return

        selected_label = self.patient_id_var.get()
        patient_id = self._patients_map.get(selected_label)
        if patient_id is None:
            messagebox.showerror("Validation error", "Select a valid patient.")
            return

        data = {
            "patient_id": patient_id,
            "date": self.date_var.get().strip(),
            "time": self.time_var.get().strip(),
            "doctor": self.doctor_var.get().strip(),
            "reason": self.reason_var.get().strip() or None,
            "room": self.room_var.get().strip() or None,
        }

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                if self.selected_appointment_id is None:
                    # insert
                    cur.execute(
                        """
                        INSERT INTO appointment (patient_id, appointment_date, appointment_time, doctor_name, reason, room)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            data["patient_id"],
                            data["date"],
                            data["time"],
                            data["doctor"],
                            data["reason"],
                            data["room"],
                        ),
                    )
                else:
                    # update existing
                    cur.execute(
                        """
                        UPDATE appointment
                        SET patient_id = ?, appointment_date = ?, appointment_time = ?, doctor_name = ?, reason = ?, room = ?
                        WHERE id = ?
                        """,
                        (
                            data["patient_id"],
                            data["date"],
                            data["time"],
                            data["doctor"],
                            data["reason"],
                            data["room"],
                            self.selected_appointment_id,
                        ),
                    )
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not save appointment: {exc}")
            return

        self._clear_form()
        self.selected_appointment_id = None
        self._load_appointments()

    def _on_delete(self) -> None:
        if self.selected_appointment_id is None:
            messagebox.showwarning("Delete appointment", "Select an appointment first.")
            return

        if not messagebox.askyesno("Delete appointment", "Are you sure you want to delete this appointment?"):
            return

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM appointment WHERE id = ?", (self.selected_appointment_id,))
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not delete appointment: {exc}")
            return

        self._clear_form()
        self.selected_appointment_id = None
        self._load_appointments()

    def _on_select_row(self, event: tk.Event | None = None) -> None:
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return

        appt_id, patient_name, date, time_str, doctor, room = values
        self.selected_appointment_id = int(appt_id)

        # set date/time/doctor/room directly
        self.date_var.set(date)
        self.time_var.set(time_str)
        self.doctor_var.set(doctor or "")
        self.room_var.set(room or "")

        # fetch reason + patient_id from DB
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT reason, patient_id FROM appointment WHERE id = ?", (self.selected_appointment_id,))
            row = cur.fetchone()
            if row:
                reason, patient_id = row
                self.reason_var.set(reason or "")

                # set combobox to matching patient label
                label_to_select = None
                for label, pid in self._patients_map.items():
                    if pid == patient_id:
                        label_to_select = label
                        break
                if label_to_select is not None:
                    self.patient_combo.set(label_to_select)

    def _on_search(self) -> None:
        term = self.search_var.get().strip()
        self._load_appointments(term or None)

    def _on_clear_search(self) -> None:
        self.search_var.set("")
        self._load_appointments()

    def _validate_form(self) -> bool:
        if not self.patient_id_var.get():
            messagebox.showerror("Validation error", "Please select a patient.")
            return False

        date_str = self.date_var.get().strip()
        time_str = self.time_var.get().strip()
        doctor = self.doctor_var.get().strip()

        if not date_str or not time_str or not doctor:
            messagebox.showerror("Validation error", "Date, time and doctor are required.")
            return False

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation error", "Date must be in format YYYY-MM-DD.")
            return False

        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Validation error", "Time must be in format HH:MM (24-hour).")
            return False

        return True

    def _clear_form(self) -> None:
        self.date_var.set("")
        self.time_var.set("")
        self.doctor_var.set("")
        self.reason_var.set("")
        self.room_var.set("")
        self.selected_appointment_id = None
