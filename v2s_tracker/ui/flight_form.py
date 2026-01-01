import customtkinter as ctk
from v2s_tracker.settings import SettingsManager

class FlightForm(ctk.CTkFrame):
    def __init__(self, master, sim_manager):
        super().__init__(master)
        self.sim_manager = sim_manager

        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(self, text="New Flight Dispatch", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Inputs
        self.pilot_id = ctk.CTkEntry(self, placeholder_text="Pilot ID (e.g. VA123)")
        self.pilot_id.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Load Saved Pilot ID
        saved_id = SettingsManager.get("pilot_id", "")
        if saved_id:
            self.pilot_id.insert(0, saved_id)

        self.callsign = ctk.CTkEntry(self, placeholder_text="Callsign (e.g. VA101)")
        self.callsign.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.aircraft = ctk.CTkEntry(self, placeholder_text="Aircraft (e.g. B738)")
        self.aircraft.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Sync Button
        self.sync_btn = ctk.CTkButton(self, text="Sync from Sim (Callsign/Type)", command=self.sync_from_sim, fg_color="gray", width=200)
        self.sync_btn.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="e")

        self.dep_entry = ctk.CTkEntry(self, placeholder_text="Departure (ICAO)")
        self.dep_entry.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.arr_entry = ctk.CTkEntry(self, placeholder_text="Arrival (ICAO)")
        self.arr_entry.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.cruise = ctk.CTkEntry(self, placeholder_text="Cruise Altitude (ft)")
        self.cruise.grid(row=7, column=0, padx=20, pady=10, sticky="ew")

        # Sim Selection
        self.sim_option = ctk.CTkOptionMenu(self, values=["Auto Detect", "X-Plane (UDP)", "MSFS (SimConnect)"], command=self.change_sim)
        self.sim_option.grid(row=8, column=0, padx=20, pady=20, sticky="ew")

        self.start_btn = ctk.CTkButton(self, text="Start Tracking", command=self.submit)
        self.start_btn.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

    def change_sim(self, choice):
        if "X-Plane" in choice:
            self.sim_manager.set_mode("xplane")
        elif "MSFS" in choice:
            self.sim_manager.set_mode("msfs")
        else:
            self.sim_manager.set_mode("auto")

    def sync_from_sim(self):
        # Ask SimManager for metadata
        meta = self.sim_manager.get_sim_metadata()
        if meta:
            if meta.get("callsign"):
                self.callsign.delete(0, "end")
                self.callsign.insert(0, meta["callsign"])
            if meta.get("aircraft"):
                self.aircraft.delete(0, "end")
                self.aircraft.insert(0, meta["aircraft"])
        else:
            print("No Sim Data Available")

    def submit(self):
        # Basic validation
        pid = self.pilot_id.get()
        cs = self.callsign.get()
        ac = self.aircraft.get()
        dep = self.dep_entry.get()
        arr = self.arr_entry.get()
        try:
            cruise = int(self.cruise.get())
        except:
            cruise = 30000

        if not pid or not dep or not arr:
            print("Missing Fields")
            return

        # Save Pilot ID
        SettingsManager.set("pilot_id", pid)

        print(f"Starting Flight {cs} ({dep}-{arr})")
        self.sim_manager.start_flight(pid, cs, ac, dep, arr, cruise)
        
        # Switch to Dashboard
        self.master.show_dashboard()
