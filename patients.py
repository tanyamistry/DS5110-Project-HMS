import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from db import get_connection


class PatientWindow(tk.Toplevel):
    """
    Window that allows the admin to create, edit and delete patients.

    Patients are stored in the `patient` table and linked to appointments.
    """

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Patient Registry")
        self.geometry("1100x650")
        self.configure(bg="#f4fbff")

        self.mrn_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.dob_var = tk.StringVar()
        self.sex_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.doctor_var = tk.StringVar()

        self.search_var = tk.StringVar()

        self.selected_patient_id: int | None = None

        self._build_ui()
        self._load_patients()

    def _build_ui(self) -> None:
        header = ttk.Label(self, text="Patient registry", font=("Segoe UI", 18, "bold"))
        header.pack(pady=(10, 5))

        main = ttk.Frame(self, padding=10)
        main.pack(expand=True, fill="both")

        # Left: form
        form = ttk.LabelFrame(main, text="Patient details", padding=10)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        labels = [
            "MRN",
            "Full name",
            "Date of birth (YYYY-MM-DD)",
            "Sex",
            "Phone",
            "Email",
            "Address",
            "Primary doctor",
        ]
        vars_ = [
            self.mrn_var,
            self.name_var,
            self.dob_var,
            self.sex_var,
            self.phone_var,
            self.email_var,
            self.address_var,
            self.doctor_var,
        ]

        for idx, (label_text, var) in enumerate(zip(labels, vars_)):
            ttk.Label(form, text=label_text).grid(row=idx, column=0, sticky="w", pady=3)
            entry = ttk.Entry(form, textvariable=var, width=35)
            entry.grid(row=idx, column=1, sticky="ew", pady=3)

        form.columnconfigure(1, weight=1)

        button_bar = ttk.Frame(form)
        button_bar.grid(row=len(labels), column=0, columnspan=2, pady=(10, 0))

        ttk.Button(button_bar, text="New", command=self._reset_form).grid(row=0, column=0, padx=5)
        ttk.Button(button_bar, text="Save", command=self._on_save).grid(row=0, column=1, padx=5)
        ttk.Button(button_bar, text="Delete", command=self._on_delete).grid(row=0, column=2, padx=5)

        # Right: table + search
        table_frame = ttk.LabelFrame(main, text="Patients", padding=10)
        table_frame.grid(row=0, column=1, sticky="nsew")

        search_row = ttk.Frame(table_frame)
        search_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(search_row, text="Search (name / MRN / phone):").pack(side="left")
        search_entry = ttk.Entry(search_row, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=5)
        ttk.Button(search_row, text="Go", command=self._on_search).pack(side="left")
        ttk.Button(search_row, text="Clear", command=self._on_clear_search).pack(side="left", padx=(5, 0))

        columns = ("id", "mrn", "name", "dob", "sex", "phone", "doctor")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
        )

        headings = {
            "id": "ID",
            "mrn": "MRN",
            "name": "Name",
            "dob": "DOB",
            "sex": "Sex",
            "phone": "Phone",
            "doctor": "Primary doctor",
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100 if col != "name" else 150, anchor="center")

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

    # ------------------------------------------------------------------ DB helpers

    def _load_patients(self, search: str | None = None) -> None:
        self.tree.delete(*self.tree.get_children())
        with get_connection() as conn:
            cur = conn.cursor()
            base_sql = (
                "SELECT id, mrn, full_name, date_of_birth, sex, phone, primary_doctor FROM patient"
            )
            params: tuple = ()
            if search:
                like = f"%{search.strip()}%"
                base_sql += " WHERE mrn LIKE ? OR full_name LIKE ? OR phone LIKE ?"
                params = (like, like, like)
            base_sql += " ORDER BY full_name"
            cur.execute(base_sql, params)
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)

    def _on_search(self) -> None:
        term = self.search_var.get().strip()
        self._load_patients(term or None)

    def _on_clear_search(self) -> None:
        self.search_var.set("")
        self._load_patients()

    def _validate_form(self) -> bool:
        mrn = self.mrn_var.get().strip()
        name = self.name_var.get().strip()
        dob = self.dob_var.get().strip()
        sex = self.sex_var.get().strip()
        phone = self.phone_var.get().strip()

        if not mrn or not name or not dob or not sex or not phone:
            messagebox.showerror(
                "Validation error",
                "MRN, Full name, Date of birth, Sex and Phone are required.",
            )
            return False

        # basic date validation
        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation error", "Date of birth must be in format YYYY-MM-DD.")
            return False

        if not phone.isdigit() or len(phone) < 7:
            messagebox.showerror("Validation error", "Phone number must contain digits only.")
            return False

        return True

    def _on_save(self) -> None:
        if not self._validate_form():
            return

        data = {
            "mrn": self.mrn_var.get().strip(),
            "full_name": self.name_var.get().strip(),
            "dob": self.dob_var.get().strip(),
            "sex": self.sex_var.get().strip(),
            "phone": self.phone_var.get().strip(),
            "email": self.email_var.get().strip() or None,
            "address": self.address_var.get().strip(),
            "doctor": self.doctor_var.get().strip() or None,
        }

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                if self.selected_patient_id is None:
                    cur.execute(
                        """
                        INSERT INTO patient (mrn, full_name, date_of_birth, sex, phone, email, address, primary_doctor)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            data["mrn"],
                            data["full_name"],
                            data["dob"],
                            data["sex"],
                            data["phone"],
                            data["email"],
                            data["address"],
                            data["doctor"],
                        ),
                    )
                else:
                    cur.execute(
                        """
                        UPDATE patient
                        SET mrn = ?, full_name = ?, date_of_birth = ?, sex = ?, phone = ?, email = ?, address = ?, primary_doctor = ?
                        WHERE id = ?
                        """,
                        (
                            data["mrn"],
                            data["full_name"],
                            data["dob"],
                            data["sex"],
                            data["phone"],
                            data["email"],
                            data["address"],
                            data["doctor"],
                            self.selected_patient_id,
                        ),
                    )
                conn.commit()
        except Exception as exc:  # sqlite3.Error, but keep generic for now
            messagebox.showerror("Database error", f"Could not save patient: {exc}")
            return

        self._reset_form()
        self._load_patients()

    def _on_delete(self) -> None:
        if self.selected_patient_id is None:
            messagebox.showwarning("Delete patient", "Select a patient first.")
            return

        if not messagebox.askyesno("Delete patient", "Are you sure you want to delete this patient?"):
            return

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM patient WHERE id = ?", (self.selected_patient_id,))
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not delete patient: {exc}")
            return

        self._reset_form()
        self._load_patients()

    def _reset_form(self) -> None:
        self.selected_patient_id = None
        for var in [
            self.mrn_var,
            self.name_var,
            self.dob_var,
            self.sex_var,
            self.phone_var,
            self.email_var,
            self.address_var,
            self.doctor_var,
        ]:
            var.set("")

    # ------------------------------------------------------------------ UI events

    def _on_select_row(self, event: tk.Event) -> None:
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return

        (
            patient_id,
            mrn,
            name,
            dob,
            sex,
            phone,
            doctor,
        ) = values

        self.selected_patient_id = int(patient_id)
        self.mrn_var.set(mrn)
        self.name_var.set(name)
        self.dob_var.set(dob)
        self.sex_var.set(sex)
        self.phone_var.set(phone)
        # we don't load address/email here since they are not in the table view;
        # fetch full row:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT email, address, primary_doctor FROM patient WHERE id = ?",
                (self.selected_patient_id,),
            )
            row = cur.fetchone()
            if row:
                email, address, primary_doctor = row
                self.email_var.set(email or "")
                self.address_var.set(address or "")
                self.doctor_var.set(primary_doctor or "")
