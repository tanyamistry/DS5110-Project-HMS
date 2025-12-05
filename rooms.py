import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from db import get_connection


class RoomAssignmentWindow(tk.Toplevel):
    """
    Manage room assignments for patients.

    Each record links a patient to a room with a date range and a daily rate.
    """

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Room assignments")
        self.geometry("1100x650")
        self.configure(bg="#f4fbff")

        self.patient_var = tk.StringVar()
        self.room_number_var = tk.StringVar()
        self.room_type_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.daily_rate_var = tk.StringVar()

        self._patients_map: dict[str, int] = {}  # "MRN - Name" -> patient_id

        self._build_ui()
        self._load_patients()
        self._load_assignments()

    def _build_ui(self) -> None:
        header = ttk.Label(self, text="Room assignments", font=("Segoe UI", 18, "bold"))
        header.pack(pady=(10, 5))

        main = ttk.Frame(self, padding=10)
        main.pack(expand=True, fill="both")

        form = ttk.LabelFrame(main, text="New room assignment", padding=10)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(form, text="Patient").grid(row=0, column=0, sticky="w", pady=3)
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_var, state="readonly", width=35)
        self.patient_combo.grid(row=0, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Room number").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.room_number_var).grid(row=1, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Room type").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.room_type_var).grid(row=2, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Start date (YYYY-MM-DD)").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.start_date_var).grid(row=3, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="End date (optional)").grid(row=4, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.end_date_var).grid(row=4, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Daily rate").grid(row=5, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.daily_rate_var).grid(row=5, column=1, sticky="ew", pady=3)

        form.columnconfigure(1, weight=1)

        ttk.Button(form, text="Create assignment", command=self._on_create).grid(
            row=6, column=0, columnspan=2, pady=(10, 0)
        )

        # table
        table_frame = ttk.LabelFrame(main, text="Current room assignments", padding=10)
        table_frame.grid(row=0, column=1, sticky="nsew")

        columns = ("id", "patient", "room", "type", "start", "end", "rate")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        headings = {
            "id": "ID",
            "patient": "Patient",
            "room": "Room",
            "type": "Type",
            "start": "Start",
            "end": "End",
            "rate": "Daily rate",
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100 if col not in ("patient",) else 150, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        # delete button
        delete_btn = ttk.Button(table_frame, text="Delete selected", command=self._on_delete)
        delete_btn.grid(row=1, column=0, sticky="w", pady=(8, 0))

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

    # ------------------------------------------------------------------ helpers

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

    def _load_assignments(self) -> None:
        self.tree.delete(*self.tree.get_children())
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT ra.id,
                       p.full_name,
                       ra.room_number,
                       ra.room_type,
                       ra.start_date,
                       COALESCE(ra.end_date, ''),
                       ra.daily_rate
                FROM room_assignment ra
                JOIN patient p ON ra.patient_id = p.id
                ORDER BY ra.start_date DESC
                """
            )
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)

    # ------------------------------------------------------------------ actions

    def _validate(self) -> bool:
        if not self.patient_var.get():
            messagebox.showerror("Validation error", "Please select a patient.")
            return False

        if not self.room_number_var.get().strip():
            messagebox.showerror("Validation error", "Room number is required.")
            return False

        sd = self.start_date_var.get().strip()
        if not sd:
            messagebox.showerror("Validation error", "Start date is required.")
            return False

        try:
            datetime.strptime(sd, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation error", "Start date must be in format YYYY-MM-DD.")
            return False

        ed = self.end_date_var.get().strip()
        if ed:
            try:
                datetime.strptime(ed, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation error", "End date must be in format YYYY-MM-DD.")
                return False

        rate_str = self.daily_rate_var.get().strip()
        if not rate_str:
            messagebox.showerror("Validation error", "Daily rate is required.")
            return False
        try:
            float(rate_str)
        except ValueError:
            messagebox.showerror("Validation error", "Daily rate must be a number.")
            return False

        return True

    def _on_create(self) -> None:
        if not self._validate():
            return

        label = self.patient_var.get()
        patient_id = self._patients_map.get(label)
        if patient_id is None:
            messagebox.showerror("Validation error", "Select a valid patient.")
            return

        data = {
            "patient_id": patient_id,
            "room_number": self.room_number_var.get().strip(),
            "room_type": self.room_type_var.get().strip() or None,
            "start_date": self.start_date_var.get().strip(),
            "end_date": self.end_date_var.get().strip() or None,
            "daily_rate": float(self.daily_rate_var.get().strip()),
        }

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO room_assignment (patient_id, room_number, room_type, start_date, end_date, daily_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["patient_id"],
                        data["room_number"],
                        data["room_type"],
                        data["start_date"],
                        data["end_date"],
                        data["daily_rate"],
                    ),
                )
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not create room assignment: {exc}")
            return

        self._clear_form()
        self._load_assignments()

    def _clear_form(self) -> None:
        self.room_number_var.set("")
        self.room_type_var.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.daily_rate_var.set("")

    def _on_delete(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Delete assignment", "Select a row first.")
            return

        item_id = selection[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return

        assignment_id = values[0]

        if not messagebox.askyesno("Delete assignment", "Are you sure you want to delete this assignment?"):
            return

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM room_assignment WHERE id = ?", (assignment_id,))
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not delete room assignment: {exc}")
            return

        self._load_assignments()
