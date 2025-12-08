from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from db import get_connection
from ui import apply_theme, maximize_window, build_header


class AppointmentsWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.title("Appointments")

        apply_theme(self)
        maximize_window(self)

        self.search_var = tk.StringVar()
        self.selected_id: int | None = None

        self.patient_label_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.doctor_var = tk.StringVar()
        self.reason_var = tk.StringVar()
        self.room_var = tk.StringVar()
        self.status_var = tk.StringVar(value="SCHEDULED")
        self.department_var = tk.StringVar()

        self._patients_map: dict[str, int] = {}

        self._build_ui()
        self._load_patients_combo()
        self._load_rows()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=18)
        container.pack(expand=True, fill="both")

        header = build_header(container, "Appointments", "Schedule and track visits")
        header.pack(fill="x", pady=(0, 10))

        main = ttk.Frame(container)
        main.pack(expand=True, fill="both")

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(main, text="Appointment details", padding=14)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(form, text="Patient").grid(row=0, column=0, sticky="w", pady=4)
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_label_var, state="readonly", width=28)
        self.patient_combo.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.date_var).grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Time (HH:MM)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.time_var).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Doctor").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.doctor_var).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Reason").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.reason_var).grid(row=4, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Room").grid(row=5, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.room_var).grid(row=5, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Status").grid(row=6, column=0, sticky="w", pady=4)
        self.status_combo = ttk.Combobox(
            form,
            textvariable=self.status_var,
            state="readonly",
            values=["SCHEDULED", "COMPLETED", "CANCELLED", "NO_SHOW"],
            width=24,
        )
        self.status_combo.grid(row=6, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Department").grid(row=7, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.department_var).grid(row=7, column=1, sticky="ew", pady=4)

        form.columnconfigure(1, weight=1)

        button_row = ttk.Frame(form)
        button_row.grid(row=8, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(button_row, text="New", style="Secondary.TButton", command=self._on_new).pack(side="left", padx=4)
        ttk.Button(button_row, text="Save", style="Accent.TButton", command=self._on_save).pack(side="left", padx=4)
        ttk.Button(button_row, text="Delete", style="Danger.TButton", command=self._on_delete).pack(side="left", padx=4)

        table_frame = ttk.LabelFrame(main, text="Appointments", padding=10)
        table_frame.grid(row=0, column=1, sticky="nsew")

        search_row = ttk.Frame(table_frame)
        search_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(search_row, text="Search (patient / doctor / status):").pack(side="left")
        ttk.Entry(search_row, textvariable=self.search_var, width=32).pack(side="left", padx=6)
        ttk.Button(search_row, text="Go", style="Secondary.TButton", command=self._on_search).pack(side="left")
        ttk.Button(search_row, text="Clear", style="Secondary.TButton", command=self._on_clear).pack(side="left", padx=(6, 0))

        columns = ("id", "patient", "date", "time", "doctor", "status", "department", "room", "reason")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        headers = [
            ("id", "ID", 60),
            ("patient", "Patient", 180),
            ("date", "Date", 100),
            ("time", "Time", 80),
            ("doctor", "Doctor", 140),
            ("status", "Status", 110),
            ("department", "Department", 140),
            ("room", "Room", 80),
            ("reason", "Reason", 200),
        ]
        for col, title, width in headers:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")

        table_frame.rowconfigure(1, weight=1)
        table_frame.columnconfigure(0, weight=1)

    def _load_patients_combo(self) -> None:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, mrn, full_name FROM patient ORDER BY full_name")
            rows = cur.fetchall()

        self._patients_map.clear()
        labels = []
        for pid, mrn, name in rows:
            label = f"{mrn} - {name}"
            self._patients_map[label] = pid
            labels.append(label)

        self.patient_combo["values"] = labels
        if labels and not self.patient_label_var.get():
            self.patient_label_var.set(labels[0])

    def _load_rows(self, search: str | None = None) -> None:
        self.tree.delete(*self.tree.get_children())
        with get_connection() as conn:
            cur = conn.cursor()
            sql = (
                "SELECT a.id, p.full_name, a.appointment_date, a.appointment_time, "
                "a.doctor_name, a.status, COALESCE(a.department,''), COALESCE(a.room,''), COALESCE(a.reason,'') "
                "FROM appointment a JOIN patient p ON a.patient_id = p.id"
            )
            params = ()
            if search:
                like = f"%{search.strip()}%"
                sql += " WHERE p.full_name LIKE ? OR a.doctor_name LIKE ? OR a.status LIKE ?"
                params = (like, like, like)
            sql += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
            cur.execute(sql, params)
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)

    def _clear_form(self) -> None:
        self.selected_id = None
        self.date_var.set("")
        self.time_var.set("")
        self.doctor_var.set("")
        self.reason_var.set("")
        self.room_var.set("")
        self.status_var.set("SCHEDULED")
        self.department_var.set("")

    def _on_new(self) -> None:
        self._clear_form()

    def _validate(self) -> bool:
        if not self.patient_label_var.get().strip():
            messagebox.showerror("Validation error", "Patient is required.")
            return False
        if not self.date_var.get().strip() or not self.time_var.get().strip():
            messagebox.showerror("Validation error", "Date and time are required.")
            return False
        if not self.doctor_var.get().strip():
            messagebox.showerror("Validation error", "Doctor is required.")
            return False
        return True

    def _on_save(self) -> None:
        if not self._validate():
            return
        pid = self._patients_map.get(self.patient_label_var.get())
        if pid is None:
            messagebox.showerror("Validation error", "Select a valid patient.")
            return

        data = (
            pid,
            self.date_var.get().strip(),
            self.time_var.get().strip(),
            self.doctor_var.get().strip(),
            self.reason_var.get().strip() or None,
            self.room_var.get().strip() or None,
            self.status_var.get().strip(),
            self.department_var.get().strip() or None,
        )

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                if self.selected_id is None:
                    cur.execute(
                        """
                        INSERT INTO appointment
                            (patient_id, appointment_date, appointment_time, doctor_name, reason, room, status, department, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                        """,
                        data,
                    )
                else:
                    cur.execute(
                        """
                        UPDATE appointment
                        SET patient_id=?, appointment_date=?, appointment_time=?, doctor_name=?, reason=?, room=?, status=?, department=?
                        WHERE id=?
                        """,
                        (*data, self.selected_id),
                    )
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not save appointment: {exc}")
            return

        self._clear_form()
        self._load_rows()

    def _on_delete(self) -> None:
        if self.selected_id is None:
            messagebox.showwarning("Delete appointment", "Select a row first.")
            return
        if not messagebox.askyesno("Delete appointment", "Are you sure you want to delete this appointment?"):
            return
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM appointment WHERE id=?", (self.selected_id,))
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not delete appointment: {exc}")
            return

        self._clear_form()
        self._load_rows()

    def _on_select(self, event=None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if not values:
            return
        appt_id, patient_name, date, time, doctor, status, dept, room, reason = values
        self.selected_id = int(appt_id)

        self.date_var.set(date)
        self.time_var.set(time)
        self.doctor_var.set(doctor)
        self.status_var.set(status)
        self.department_var.set(dept or "")
        self.room_var.set(room or "")
        self.reason_var.set(reason or "")

        label_to_select = None
        for label in self._patients_map.keys():
            if label.endswith(f"- {patient_name}"):
                label_to_select = label
                break
        if label_to_select:
            self.patient_combo.set(label_to_select)

    def _on_search(self) -> None:
        term = self.search_var.get().strip()
        self._load_rows(term or None)

    def _on_clear(self) -> None:
        self.search_var.set("")
        self._load_rows()
