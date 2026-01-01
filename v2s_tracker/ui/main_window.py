import customtkinter as ctk
from v2s_tracker.config import Config
from v2s_tracker.ui.dashboard import Dashboard
from v2s_tracker.ui.flight_form import FlightForm
from v2s_tracker.sim.manager import SimManager

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(Config.APP_NAME)
        self.geometry("1100x700")
        
        # Grid Configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Simulator Manager
        self.sim_manager = SimManager()

        # Navigation Frame
        self.nav_frame = ctk.CTkFrame(self, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame_label = ctk.CTkLabel(self.nav_frame, text="V2S ACARS", font=ctk.CTkFont(size=20, weight="bold"))
        self.nav_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = ctk.CTkButton(self.nav_frame, text="Dashboard", command=self.show_dashboard, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.home_button.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        self.dispatch_button = ctk.CTkButton(self.nav_frame, text="Dispatch", command=self.show_dispatch, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.dispatch_button.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        # Connection Status (Footer of sidebar)
        self.status_label = ctk.CTkLabel(self.nav_frame, text="SIM: DISCONNECTED", font=("Consolas", 12), text_color="gray")
        self.status_label.grid(row=10, column=0, padx=20, pady=20, sticky="s")
        self.nav_frame.grid_rowconfigure(10, weight=1)

        # Pages
        self.dashboard = Dashboard(self, self.sim_manager)
        self.flight_form = FlightForm(self, self.sim_manager)

        # Start on Dashboard
        self.show_dashboard()

        # Telemetry Loop
        self.after(500, self.update_telemetry)

    def show_dashboard(self):
        self.select_frame_by_name("dashboard")

    def show_dispatch(self):
        self.select_frame_by_name("dispatch")

    def select_frame_by_name(self, name):
        # set button color
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "dashboard" else "transparent")
        self.dispatch_button.configure(fg_color=("gray75", "gray25") if name == "dispatch" else "transparent")

        # show selected frame
        if name == "dashboard":
            self.dashboard.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        else:
            self.dashboard.grid_forget()
        
        if name == "dispatch":
            self.flight_form.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        else:
            self.flight_form.grid_forget()

    def update_telemetry(self):
        # Tick the sim manager
        telemetry = self.sim_manager.tick()
        
        # Update Dashboard
        if telemetry:
            self.dashboard.update_data(telemetry)
            self.status_label.configure(text=f"SIM: {telemetry.get('source', 'UNKNOWN')}", text_color=Config.COLOR_SUCCESS)
        else:
            self.status_label.configure(text="SIM: DISCONNECTED", text_color="gray")

        # Re-schedule
        self.after(250, self.update_telemetry)
