import tkinter as tk
from tkinter import ttk, messagebox

from ui import apply_theme, maximize_window, build_header
from db import init_db
from patients import PatientsWindow
from appointments import AppointmentsWindow
from rooms import RoomsWindow
from treatments import TreatmentsWindow
from billing import BillingWindow


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System - Login")

        apply_theme(self)
        maximize_window(self)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        container = ttk.Frame(self, padding=24)
        container.pack(expand=True, fill="both")

        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        card = ttk.Frame(container, padding=28, style="TFrame")
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)

        header = build_header(card, "CityCare General Hospital", "Administrator portal")
        header.grid(row=0, column=0, sticky="w", pady=(0, 18))

        form = ttk.Frame(card)
        form.grid(row=1, column=0, sticky="n", pady=(10, 0))

        ttk.Label(form, text="Username").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.username_var, width=30).grid(row=1, column=0, sticky="w")

        ttk.Label(form, text="Password").grid(row=2, column=0, sticky="w", pady=(18, 6))
        ttk.Entry(form, textvariable=self.password_var, width=30, show="*").grid(row=3, column=0, sticky="w")

        login_btn = ttk.Button(form, text="Sign in", style="Accent.TButton", command=self._on_login)
        login_btn.grid(row=4, column=0, pady=(22, 0), sticky="w")

        self.bind("<Return>", lambda e: self._on_login())

    def _on_login(self):
        if self.username_var.get().strip() == ADMIN_USERNAME and self.password_var.get().strip() == ADMIN_PASSWORD:
            self.destroy()
            dash = AdminDashboard()
            dash.mainloop()
        else:
            messagebox.showerror("Login failed", "Invalid username or password.")


class AdminDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System - Admin dashboard")

        apply_theme(self)
        maximize_window(self)

        container = ttk.Frame(self, padding=24)
        container.pack(expand=True, fill="both")

        header = build_header(
            container,
            "Administration dashboard",
            "Manage patients, appointments, rooms, treatments, and billing",
        )
        header.pack(fill="x", pady=(0, 16))

        main = ttk.Frame(container)
        main.pack(expand=True, fill="both")

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        ttk.Label(left, text="Core modules", style="Subheader.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Button(left, text="Patients", style="Accent.TButton", command=self._open_patients, width=28).pack(anchor="w", pady=4)
        ttk.Button(left, text="Appointments", style="Accent.TButton", command=self._open_appointments, width=28).pack(anchor="w", pady=4)
        ttk.Button(left, text="Room assignments", style="Accent.TButton", command=self._open_rooms, width=28).pack(anchor="w", pady=4)

        ttk.Label(right, text="Clinical and billing", style="Subheader.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Button(right, text="Treatments", style="Accent.TButton", command=self._open_treatments, width=28).pack(anchor="w", pady=4)
        ttk.Button(right, text="Billing & invoices", style="Accent.TButton", command=self._open_billing, width=28).pack(anchor="w", pady=4)

        bottom = ttk.Frame(container)
        bottom.pack(fill="x", pady=(18, 0))
        ttk.Label(bottom, text="Logged in as: admin", style="Subheader.TLabel").pack(side="left")
        ttk.Button(bottom, text="Exit", style="Secondary.TButton", command=self.destroy).pack(side="right")

    def _open_patients(self):
        PatientsWindow(self)

    def _open_appointments(self):
        AppointmentsWindow(self)

    def _open_rooms(self):
        RoomsWindow(self)

    def _open_treatments(self):
        TreatmentsWindow(self)

    def _open_billing(self):
        BillingWindow(self)


if __name__ == "__main__":
    init_db()
    app = LoginWindow()
    app.mainloop()
