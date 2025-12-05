import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from db import get_connection


class TreatmentWindow(tk.Toplevel):
    """
    Manage treatments or procedures for patients.
    """

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Treatments")
        self.geometry("1100x650")
        self.configure(bg="#f4fbff")

        self.patient_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.cost_var = tk.StringVar()

        self._patients_map: dict[str, int] = {}

        self._build_ui()
        self._load_patients()
        self._load_treatments()

    def _build_ui(self) -> None:
        header = ttk.Label(self, text="Treatments", font=("Segoe UI", 18, "bold"))
        header.pack(pady=(10, 5))

        main = ttk.Frame(self, padding=10)
        main.pack(expand=True, fill="both")

        form = ttk.LabelFrame(main, text="New treatment", padding=10)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(form, text="Patient").grid(row=0, column=0, sticky="w", pady=3)
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_var, state="readonly", width=35)
        self.patient_combo.grid(row=0, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.date_var).grid(row=1, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Description").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.description_var).grid(row=2, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Cost").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.cost_var).grid(row=3, column=1, sticky="ew", pady=3)

        form.columnconfigure(1, weight=1)

        ttk.Button(form, text="Add treatment", command=self._on_add).grid(
            row=4, column=0, columnspan=2, pady=(10, 0)
        )

        # table
        table_frame = ttk.LabelFrame(main, text="Treatments", padding=10)
        table_frame.grid(row=0, column=1, sticky="nsew")

        columns = ("id", "patient", "date", "description", "cost")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        headings = {
            "id": "ID",
            "patient": "Patient",
            "date": "Date",
            "description": "Description",
            "cost": "Cost",
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100 if col not in ("patient", "description") else 180, anchor="center")

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

    def _load_treatments(self) -> None:
        self.tree.delete(*self.tree.get_children())
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT t.id,
                       p.full_name,
                       t.treatment_date,
                       t.description,
                       t.cost
                FROM treatment t
                JOIN patient p ON t.patient_id = p.id
                ORDER BY t.treatment_date DESC
                """
            )
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)

    # ------------------------------------------------------------------ actions

    def _validate(self) -> bool:
        if not self.patient_var.get():
            messagebox.showerror("Validation error", "Please select a patient.")
            return False

        date_str = self.date_var.get().strip()
        if not date_str:
            messagebox.showerror("Validation error", "Date is required.")
            return False

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation error", "Date must be in format YYYY-MM-DD.")
            return False

        desc = self.description_var.get().strip()
        if not desc:
            messagebox.showerror("Validation error", "Description is required.")
            return False

        cost_str = self.cost_var.get().strip()
        if not cost_str:
            messagebox.showerror("Validation error", "Cost is required.")
            return False
        try:
            float(cost_str)
        except ValueError:
            messagebox.showerror("Validation error", "Cost must be a number.")
            return False

        return True

    def _on_add(self) -> None:
        if not self._validate():
            return

        label = self.patient_var.get()
        patient_id = self._patients_map.get(label)
        if patient_id is None:
            messagebox.showerror("Validation error", "Select a valid patient.")
            return

        data = {
            "patient_id": patient_id,
            "date": self.date_var.get().strip(),
            "description": self.description_var.get().strip(),
            "cost": float(self.cost_var.get().strip()),
        }

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO treatment (patient_id, treatment_date, description, cost)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        data["patient_id"],
                        data["date"],
                        data["description"],
                        data["cost"],
                    ),
                )
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not add treatment: {exc}")
            return

        self._clear_form()
        self._load_treatments()

    def _clear_form(self) -> None:
        self.date_var.set("")
        self.description_var.set("")
        self.cost_var.set("")

    def _on_delete(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Delete treatment", "Select a row first.")
            return

        item_id = selection[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return

        treatment_id = values[0]

        if not messagebox.askyesno("Delete treatment", "Are you sure you want to delete this treatment?"):
            return

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM treatment WHERE id = ?", (treatment_id,))
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not delete treatment: {exc}")
            return

        self._load_treatments()
