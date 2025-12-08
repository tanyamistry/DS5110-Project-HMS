from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from db import get_connection
from ui import apply_theme, maximize_window, build_header


class TreatmentsWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.title("Treatments")

        apply_theme(self)
        maximize_window(self)

        self.search_var = tk.StringVar()
        self.selected_id: int | None = None

        self.patient_name_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.cost_var = tk.StringVar()

        self._build_ui()
        self._load_rows()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=18)
        container.pack(expand=True, fill="both")

        header = build_header(container, "Treatments", "Record procedures and costs")
        header.pack(fill="x", pady=(0, 10))

        main = ttk.Frame(container)
        main.pack(expand=True, fill="both")

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(main, text="Treatment details", padding=14)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        fields = [
            ("Patient name (for lookup)", self.patient_name_var),
            ("Treatment date (YYYY-MM-DD)", self.date_var),
            ("Description", self.description_var),
            ("Cost", self.cost_var),
        ]
        for row, (label, var) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=var).grid(row=row, column=1, sticky="ew", pady=4)

        form.columnconfigure(1, weight=1)

        button_row = ttk.Frame(form)
        button_row.grid(row=len(fields), column=0, columnspan=2, pady=(12, 0))
        ttk.Button(button_row, text="New", style="Secondary.TButton", command=self._on_new).pack(side="left", padx=4)
        ttk.Button(button_row, text="Save", style="Accent.TButton", command=self._on_save).pack(side="left", padx=4)
        ttk.Button(button_row, text="Delete", style="Danger.TButton", command=self._on_delete).pack(side="left", padx=4)

        table_frame = ttk.LabelFrame(main, text="Treatments", padding=10)
        table_frame.grid(row=0, column=1, sticky="nsew")

        search_row = ttk.Frame(table_frame)
        search_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(search_row, text="Search (patient / description):").pack(side="left")
        ttk.Entry(search_row, textvariable=self.search_var, width=32).pack(side="left", padx=6)
        ttk.Button(search_row, text="Go", style="Secondary.TButton", command=self._on_search).pack(side="left")
        ttk.Button(search_row, text="Clear", style="Secondary.TButton", command=self._on_clear).pack(side="left", padx=(6, 0))

        columns = ("id", "patient", "date", "description", "cost")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        headers = [
            ("id", "ID", 60),
            ("patient", "Patient", 180),
            ("date", "Date", 100),
            ("description", "Description", 260),
            ("cost", "Cost", 80),
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
            sql = (
                "SELECT t.id, p.full_name, t.treatment_date, t.description, t.cost "
                "FROM treatment t JOIN patient p ON t.patient_id = p.id"
            )
            params = ()
            if search:
                like = f"%{search.strip()}%"
                sql += " WHERE p.full_name LIKE ? OR t.description LIKE ?"
                params = (like, like)
            sql += " ORDER BY t.treatment_date DESC"
            cur.execute(sql, params)
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)

    def _patient_name_to_id(self, name: str):
        if not name.strip():
            return None
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM patient WHERE full_name LIKE ? ORDER BY id LIMIT 1", (name.strip(),))
            row = cur.fetchone()
            return row[0] if row else None

    def _clear_form(self) -> None:
        self.selected_id = None
        self.patient_name_var.set("")
        self.date_var.set("")
        self.description_var.set("")
        self.cost_var.set("")

    def _on_new(self) -> None:
        self._clear_form()

    def _validate(self) -> bool:
        if not self.patient_name_var.get().strip():
            messagebox.showerror("Validation error", "Patient name is required for lookup.")
            return False
        if not self.date_var.get().strip():
            messagebox.showerror("Validation error", "Treatment date is required.")
            return False
        if not self.description_var.get().strip():
            messagebox.showerror("Validation error", "Description is required.")
            return False
        if not self.cost_var.get().strip():
            messagebox.showerror("Validation error", "Cost is required.")
            return False
        try:
            float(self.cost_var.get().strip())
        except ValueError:
            messagebox.showerror("Validation error", "Cost must be a number.")
            return False
        return True

    def _on_save(self) -> None:
        if not self._validate():
            return
        pid = self._patient_name_to_id(self.patient_name_var.get())
        if pid is None:
            messagebox.showerror("Lookup error", "No matching patient found for that name.")
            return

        data = (
            pid,
            self.date_var.get().strip(),
            self.description_var.get().strip(),
            float(self.cost_var.get().strip()),
        )

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                if self.selected_id is None:
                    cur.execute(
                        """
                        INSERT INTO treatment
                            (patient_id, treatment_date, description, cost, created_at)
                        VALUES (?, ?, ?, ?, datetime('now'))
                        """,
                        data,
                    )
                else:
                    cur.execute(
                        """
                        UPDATE treatment
                        SET patient_id=?, treatment_date=?, description=?, cost=?
                        WHERE id=?
                        """,
                        (*data, self.selected_id),
                    )
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not save treatment: {exc}")
            return

        self._clear_form()
        self._load_rows()

    def _on_delete(self) -> None:
        if self.selected_id is None:
            messagebox.showwarning("Delete treatment", "Select a row first.")
            return
        if not messagebox.askyesno("Delete treatment", "Are you sure you want to delete this treatment?"):
            return
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM treatment WHERE id=?", (self.selected_id,))
                conn.commit()
        except Exception as exc:
            messagebox.showerror("Database error", f"Could not delete treatment: {exc}")
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
        tid, patient, date, desc, cost = values
        self.selected_id = int(tid)
        self.patient_name_var.set(patient)
        self.date_var.set(date)
        self.description_var.set(desc)
        self.cost_var.set(str(cost))

    def _on_search(self) -> None:
        term = self.search_var.get().strip()
        self._load_rows(term or None)

    def _on_clear(self) -> None:
        self.search_var.set("")
        self._load_rows()
