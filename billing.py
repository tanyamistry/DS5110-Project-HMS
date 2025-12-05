import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from db import get_connection


class BillingWindow(tk.Toplevel):
    """
    Very simple billing / invoice window.

    Allows the admin to create invoices for patients with a total amount,
    status, and free-text notes. It does not automatically calculate totals
    from treatments or room stays, but that could be added later.
    """

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Billing / Invoices")
        self.geometry("1100x650")
        self.configure(bg="#f4fbff")

        self.patient_var = tk.StringVar()
        self.total_var = tk.StringVar()
        self.status_var = tk.StringVar(value="OPEN")
        self.notes_var = tk.StringVar()

        self._patients_map: dict[str, int] = {}

        self._build_ui()
        self._load_patients()
        self._load_invoices()

    def _build_ui(self) -> None:
        header = ttk.Label(self, text="Billing / invoices", font=("Segoe UI", 18, "bold"))
        header.pack(pady=(10, 5))

        main = ttk.Frame(self, padding=10)
        main.pack(expand=True, fill="both")

        form = ttk.LabelFrame(main, text="New invoice", padding=10)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(form, text="Patient").grid(row=0, column=0, sticky="w", pady=3)
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_var, state="readonly", width=35)
        self.patient_combo.grid(row=0, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Total amount").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.total_var).grid(row=1, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Status").grid(row=2, column=0, sticky="w", pady=3)
        self.status_combo = ttk.Combobox(
            form,
            textvariable=self.status_var,
            values=["OPEN", "PAID", "CANCELLED"],
            state="readonly",
        )
        self.status_combo.grid(row=2, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Notes").grid(row=3, column=0, sticky="nw", pady=3)
        ttk.Entry(form, textvariable=self.notes_var).grid(row=3, column=1, sticky="ew", pady=3)

        form.columnconfigure(1, weight=1)

        ttk.Button(form, text="Create invoice", command=self._on_create).grid(
            row=4, column=0, columnspan=2, pady=(10, 0)
        )

        # table
        table_frame = ttk.LabelFrame(main, text="Invoices", padding=10)
        table_frame.grid(row=0, column=1, sticky="nsew")

        columns = ("id", "patient", "created_at", "total", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        headings = {
            "id": "ID",
            "patient": "Patient",
            "created_at": "Created at",
            "total": "Total",
            "status": "Status",
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=120 if col != "patient" else 160, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

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

    def _load_invoices(self) -> None:
        self.tree.delete(*self.tree.get_children())
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT i.id,
                       p.full_name,
                       i.created_at,
                       i.total_amount,
                       i.status
                FROM invoice i
                JOIN patient p ON i.patient_id = p.id
                ORDER BY i.created_at DESC
                """
            )
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)

    # ------------------------------------------------------------------ actions

    def _validate(self) -> bool:
        if not self.patient_var.get():
            messagebox.showerror("Validation error", "Please select a patient.")
            return False

        total_str = self.total_var.get().strip()
        if not total_str:
            messagebox.showerror("Validation error", "Total amount is required.")
            return False
        try:
            float(total_str)
        except ValueError:
            messagebox.showerror("Validation error", "Total amount must be a number.")
            return False

        if self.status_var.get() not in {"OPEN", "PAID", "CANCELLED"}:
            messagebox.showerror("Validation error", "Status must be OPEN, PAID or CANCELLED.")
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

        created_at = datetime.now().isoformat(timespec="seconds")
        total = float(self.total_var.get().strip())
        status = self.status_var.get()
        notes = self.notes_var.get().strip() or None

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO invoice (patient_id, created_at, total_amount, status, notes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (patient_id, created_at, total, status, notes),
                )
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not create invoice: {exc}")
            return

        self._clear_form()
        self._load_invoices()

    def _clear_form(self) -> None:
        self.total_var.set("")
        self.status_var.set("OPEN")
        self.notes_var.set("")

    def _on_delete(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Delete invoice", "Select a row first.")
            return

        item_id = selection[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return

        invoice_id = values[0]

        if not messagebox.askyesno("Delete invoice", "Are you sure you want to delete this invoice?"):
            return

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM invoice WHERE id = ?", (invoice_id,))
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not delete invoice: {exc}")
            return

        self._load_invoices()
