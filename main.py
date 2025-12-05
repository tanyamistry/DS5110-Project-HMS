import tkinter as tk
from tkinter import ttk, messagebox

from db import init_db, get_connection
from patients import PatientWindow
from appointments import AppointmentWindow
from rooms import RoomAssignmentWindow
from treatments import TreatmentWindow
from billing import BillingWindow


class LoginWindow(tk.Tk):
    """
    Simple login window with a single admin role.
    In a more advanced version, users could be stored in the database.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("Hospital Admin Login")
        self.geometry("520x320")
        self.resizable(False, False)

        self._configure_style()
        self._build_ui()

    def _configure_style(self) -> None:
        """
        Configure a simple hospital-like color palette for all ttk widgets.
        """
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            # fall back silently if theme is not available
            pass

        primary_bg = "#f4fbff"   # soft hospital blue
        header_bg = "#e1f0ff"
        accent = "#2a7fba"
        text_fg = "#12354a"

        # set window background
        self.configure(bg=primary_bg)

        # base widgets
        style.configure("TFrame", background=primary_bg)
        style.configure("TLabelframe", background=primary_bg, borderwidth=1)
        style.configure(
            "TLabelframe.Label",
            background=primary_bg,
            foreground=text_fg,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure("TLabel", background=primary_bg, foreground=text_fg)

        # entries
        style.configure("TEntry", fieldbackground="white")

        # buttons
        style.configure(
            "TButton",
            background=accent,
            foreground="white",
            padding=6,
            borderwidth=0,
        )
        style.map(
            "TButton",
            background=[("active", "#245f8f"), ("pressed", "#1c4c6f")],
        )

        # treeview
        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground=text_fg,
            borderwidth=0,
        )
        style.map("Treeview", background=[("selected", "#c0e6ff")])
        style.configure(
            "Treeview.Heading",
            background=header_bg,
            foreground=text_fg,
            font=("Segoe UI", 9, "bold"),
        )

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(expand=True, fill="both")

        title = ttk.Label(container, text="Hospital Administration", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(container, text="Username").grid(row=1, column=0, sticky="w")
        ttk.Label(container, text="Password").grid(row=2, column=0, sticky="w", pady=(10, 0))

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        username_entry = ttk.Entry(container, textvariable=self.username_var)
        password_entry = ttk.Entry(container, textvariable=self.password_var, show="*")

        username_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0))
        password_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=(10, 0))

        container.columnconfigure(1, weight=1)

        login_button = ttk.Button(container, text="Log in", command=self._on_login)
        login_button.grid(row=3, column=0, columnspan=2, pady=(20, 0))

    def _on_login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        # For this project we keep it simple:
        # hard-coded admin credentials.
        if username == "admin" and password == "admin":
            self.destroy()
            app = AdminDashboard()
            app.mainloop()
        else:
            messagebox.showerror("Login failed", "Invalid username or password.")


class AdminDashboard(tk.Tk):
    """
    Main admin dashboard:
    - Manage patients
    - Manage appointments
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("Hospital Administration Dashboard")
        self.geometry("500x300")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(expand=True, fill="both")

        title = ttk.Label(container, text="Admin Dashboard", font=("Segoe UI", 18, "bold"))
        title.pack(pady=(0, 20))

        btn_patients = ttk.Button(
            container,
            text="Patient Registry",
            width=25,
            command=self._open_patients,
        )
        btn_patients.pack(pady=5)

        btn_appointments = ttk.Button(
            container,
            text="Appointments",
            width=25,
            command=self._open_appointments,
        )
        btn_appointments.pack(pady=5)

        btn_rooms = ttk.Button(
            container,
            text="Room assignments",
            width=25,
            command=self._open_rooms,
        )
        btn_rooms.pack(pady=5)

        btn_treatments = ttk.Button(
            container,
            text="Treatments",
            width=25,
            command=self._open_treatments,
        )
        btn_treatments.pack(pady=5)

        btn_billing = ttk.Button(
            container,
            text="Billing / Invoices",
            width=25,
            command=self._open_billing,
        )
        btn_billing.pack(pady=5)

        btn_quit = ttk.Button(container, text="Exit", width=25, command=self.destroy)
        btn_quit.pack(pady=(20, 0))

    def _open_patients(self) -> None:
        PatientWindow(self)

    def _open_appointments(self) -> None:
        AppointmentWindow(self)

    def _open_rooms(self) -> None:
        RoomAssignmentWindow(self)

    def _open_treatments(self) -> None:
        TreatmentWindow(self)

    def _open_billing(self) -> None:
        BillingWindow(self)


if __name__ == "__main__":
    # Ensure database and tables exist before launching UI
    init_db()
    login = LoginWindow()
    login.mainloop()
