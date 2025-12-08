from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from db import get_connection
from ui import apply_theme, maximize_window, build_header
from validators import (
    validate_mrn,
    validate_required_field,
    validate_date_of_birth,
    validate_sex,
    validate_phone_number,
    validate_email,
)


class PatientsWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.title("Patients")

        apply_theme(self)
        maximize_window(self)

        self.search_var = tk.StringVar()
        self.selected_id: int | None = None

        self.mrn_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.dob_var = tk.StringVar()
        self.sex_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.primary_doctor_var = tk.StringVar()

        self._build_ui()
        self._load_rows()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=18)
        container.pack(expand=True, fill="both")

        header = build_header(container, "Patients", "Register and manage patient records")
        header.pack(fill="x", pady=(0, 10))

        main = ttk.Frame(container)
        main.pack(expand=True, fill="both")

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(main, text="Patient details", padding=14)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        labels = [
            ("MRN", self.mrn_var),
            ("Full name", self.name_var),
            ("Date of birth (YYYY-MM-DD)", self.dob_var),
            ("Sex (M/F/O)", self.sex_var),
            ("Phone", self.phone_var),
            ("Email", self.email_var),
            ("Address", self.address_var),
            ("Primary doctor", self.primary_doctor_var),
        ]
        for row, (text, var) in enumerate(labels):
            ttk.Label(form, text=text).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=var).grid(row=row, column=1, sticky="ew", pady=4)

        form.columnconfigure(1, weight=1)

        button_row = ttk.Frame(form)
        button_row.grid(row=len(labels), column=0, columnspan=2, pady=(12, 0))
        ttk.Button(button_row, text="New", style="Secondary.TButton", command=self._on_new).pack(side="left", padx=4)
        ttk.Button(button_row, text="Save", style="Accent.TButton", command=self._on_save).pack(side="left", padx=4)
        ttk.Button(button_row, text="Delete", style="Danger.TButton", command=self._on_delete).pack(side="left", padx=4)

        table_frame = ttk.LabelFrame(main, text="Patients", padding=10)
        table_frame.grid(row=0, column=1, sticky="nsew")

        search_row = ttk.Frame(table_frame)
        search_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(search_row, text="Search (name / MRN):").pack(side="left")
        ttk.Entry(search_row, textvariable=self.search_var, width=28).pack(side="left", padx=6)
        ttk.Button(search_row, text="Go", style="Secondary.TButton", command=self._on_search).pack(side="left")
        ttk.Button(search_row, text="Clear", style="Secondary.TButton", command=self._on_clear).pack(side="left", padx=(6, 0))

        columns = ("id", "mrn", "name", "dob", "sex", "phone", "email", "primary_doctor")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        headers = [
            ("id", "ID", 60),
            ("mrn", "MRN", 100),
            ("name", "Name", 180),
            ("dob", "DOB", 110),
            ("sex", "Sex", 60),
            ("phone", "Phone", 110),
            ("email", "Email", 200),
            ("primary_doctor", "Doctor", 130),
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

    def _load_rows(self, search: str | None = None) -> None:
        self.tree.delete(*self.tree.get_children())
        with get_connection() as conn:
            cur = conn.cursor()
            sql = "SELECT id, mrn, full_name, date_of_birth, sex, phone, email, primary_doctor FROM patient"
            params = ()
            if search:
                like = f"%{search.strip()}%"
                sql += " WHERE full_name LIKE ? OR mrn LIKE ?"
                params = (like, like)
            sql += " ORDER BY full_name"
            cur.execute(sql, params)
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)

    def _clear_form(self) -> None:
        self.selected_id = None
        self.mrn_var.set("")
        self.name_var.set("")
        self.dob_var.set("")
        self.sex_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_var.set("")
        self.primary_doctor_var.set("")

    def _on_new(self) -> None:
        self._clear_form()

    def _validate(self) -> bool:
        # Validate MRN
        is_valid, error_msg = validate_mrn(self.mrn_var.get())
        if not is_valid:
            messagebox.showerror("Validation error", error_msg)
            return False
        
        # Validate full name
        is_valid, error_msg = validate_required_field(self.name_var.get(), "Full name")
        if not is_valid:
            messagebox.showerror("Validation error", error_msg)
            return False
        
        # Validate date of birth
        is_valid, error_msg = validate_date_of_birth(self.dob_var.get())
        if not is_valid:
            messagebox.showerror("Validation error", error_msg)
            return False
        
        # Validate sex
        is_valid, error_msg = validate_sex(self.sex_var.get())
        if not is_valid:
            messagebox.showerror("Validation error", error_msg)
            return False
        
        # Validate phone number
        is_valid, error_msg = validate_phone_number(self.phone_var.get())
        if not is_valid:
            messagebox.showerror("Validation error", error_msg)
            return False
        
        # Validate email (optional field)
        is_valid, error_msg = validate_email(self.email_var.get())
        if not is_valid:
            messagebox.showerror("Validation error", error_msg)
            return False
        
        return True

    def _on_save(self) -> None:
        if not self._validate():
            return

        data = (
            self.mrn_var.get().strip(),
            self.name_var.get().strip(),
            self.dob_var.get().strip(),
            self.sex_var.get().strip(),
            self.phone_var.get().strip(),
            self.email_var.get().strip() or None,
            self.address_var.get().strip() or None,
            self.primary_doctor_var.get().strip() or None,
        )

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                if self.selected_id is None:
                    cur.execute(
                        """
                        INSERT INTO patient
                            (mrn, full_name, date_of_birth, sex, phone, email, address, primary_doctor, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                        """,
                        data,
                    )
                else:
                    cur.execute(
                        """
                        UPDATE patient
                        SET mrn=?, full_name=?, date_of_birth=?, sex=?, phone=?, email=?, address=?, primary_doctor=?
                        WHERE id=?
                        """,
                        (*data, self.selected_id),
                    )
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not save patient: {exc}")
            return

        self._clear_form()
        self._load_rows()

    def _on_delete(self) -> None:
        if self.selected_id is None:
            messagebox.showwarning("Delete patient", "Select a row first.")
            return
        if not messagebox.askyesno("Delete patient", "Are you sure you want to delete this patient and all related records?"):
            return
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM patient WHERE id=?", (self.selected_id,))
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not delete patient: {exc}")
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
        pid, mrn, name, dob, sex, phone, email, doctor = values
        self.selected_id = int(pid)
        self.mrn_var.set(mrn)
        self.name_var.set(name)
        self.dob_var.set(dob)
        self.sex_var.set(sex)
        self.phone_var.set(phone)
        self.email_var.set(email or "")
        self.primary_doctor_var.set(doctor or "")

    def _on_search(self) -> None:
        term = self.search_var.get().strip()
        self._load_rows(term or None)

    def _on_clear(self) -> None:
        self.search_var.set("")
        self._load_rows()
