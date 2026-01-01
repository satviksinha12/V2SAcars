import customtkinter as ctk
from v2s_tracker.config import Config

class Dashboard(ctk.CTkFrame):
    def __init__(self, master, sim_manager):
        super().__init__(master)
        self.sim_manager = sim_manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Header
        self.header = ctk.CTkLabel(self, text="Flight Telemetry", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")

        # Metric Cards
        self.alt_card = self.create_card(1, 0, "Altitude", "--- ft")
        self.speed_card = self.create_card(1, 1, "Ground Speed", "--- kts")
        self.heading_card = self.create_card(1, 2, "Heading", "---°")

        self.pos_card = self.create_card(2, 0, "Position", "---, ---")
        self.rate_card = self.create_card(2, 1, "Landing Rate", "--- fpm")
        self.status_card = self.create_card(2, 2, "Flight Phase", "Standby")

        # Action Button
        self.action_button = ctk.CTkButton(self, text="FINISH FLIGHT", command=self.on_action_button_click, 
                                           fg_color=Config.COLOR_ERROR, hover_color="#b91c1c", height=40,
                                           font=ctk.CTkFont(size=14, weight="bold"))
        self.action_button.grid(row=3, column=0, columnspan=3, padx=20, pady=20, sticky="ew")
        
        self.is_finished = False

    def create_card(self, row, col, title, value):
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        title_lbl = ctk.CTkLabel(frame, text=title.upper(), font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70")
        title_lbl.pack(pady=(15, 0))
        
        value_lbl = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=24, weight="bold"))
        value_lbl.pack(pady=(0, 15))
        
        return value_lbl

    def update_data(self, t):
        self.alt_card.configure(text=f"{int(t.get('alt', 0))} ft")
        self.speed_card.configure(text=f"{int(t.get('speed', 0))} kts")
        self.heading_card.configure(text=f"{int(t.get('heading', 0))}°")
        
        lat = t.get('lat', 0)
        lon = t.get('lon', 0)
        self.pos_card.configure(text=f"{lat:.3f}, {lon:.3f}")
        
        # Helper to show VS if approaching/landing? Or always?
        # User asked for Landing Rate specifically.
        # But during flight it's just VS.
        # Let's show VS generally, but label it "Vertical Spd" until landing?
        # User asked for "landing rate".
        # Let's show VS always for now.
        vs = int(t.get('vs', 0))
        self.rate_card.configure(text=f"{vs} fpm")
        
        phase = t.get('phase', None)
        if phase:
            self.status_card.configure(text=phase.upper(), text_color=Config.COLOR_SUCCESS)
        else:
             on_ground = t.get('onGround', True)
             self.status_card.configure(text="ON GROUND" if on_ground else "AIRBORNE", text_color="gray80")

    def on_action_button_click(self):
        if not self.is_finished:
            # Finish Flight Steps
            self.sim_manager.stop_tracking()
            self.is_finished = True
            
            # Update Button
            self.action_button.configure(text="SUBMIT PIREP", fg_color=Config.COLOR_SUCCESS, hover_color=Config.COLOR_ACCENT_HOVER)
            self.status_card.configure(text="FLIGHT FINISHED", text_color=Config.COLOR_ACCENT)
        else:
            # Submit PIREP Steps
            self.action_button.configure(state="disabled", text="SUBMITTING...")
            success = self.sim_manager.submit_pirep()
            
            if success:
                self.action_button.configure(text="PIREP SUBMITTED", fg_color="gray50")
            else:
                self.action_button.configure(text="SUBMIT FAILED - RETRY", state="normal")
