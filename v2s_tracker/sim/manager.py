from v2s_tracker.sim.xplane import XPlaneProvider
from v2s_tracker.sim.msfs import MsfsProvider
from v2s_tracker.sim.common import FlightManager
import sys

class SimManager:
    def __init__(self):
        self.mode = "auto"
        self.providers = {
            "xplane": XPlaneProvider(),
            "msfs": MsfsProvider()
        }
        self.current_provider = None
        self.flight_manager = None

    def set_mode(self, mode):
        print(f"Switching Sim Mode: {mode}")
        self.mode = mode.lower()
        
        # Stop all
        for p in self.providers.values():
            p.stop()
            
        if self.mode in self.providers:
            self.current_provider = self.providers[self.mode]
            self.current_provider.start()
            if self.flight_manager:
                self.current_provider.set_flight_manager(self.flight_manager)

    def get_sim_metadata(self):
        # Fetch metadata from active provider (if connected)
        if self.current_provider:
             return self.current_provider.get_metadata()
        return {}

    def start_flight(self, pilot_id, callsign, aircraft, dep, arr, cruise_alt):
        self.flight_manager = FlightManager(pilot_id, callsign, aircraft, dep, arr, cruise_alt)
        if self.current_provider:
            self.current_provider.set_flight_manager(self.flight_manager)
        else:
            # Auto-select if not set
            self.set_mode("xplane") # Default or try detection

    def tick(self):
        # Return telemetry for UI
        if self.flight_manager:
            return {
                "source": self.mode.upper(),
                "lat": self.flight_manager.lat,
                "lon": self.flight_manager.lon,
                "alt": self.flight_manager.alt,
                "speed": self.flight_manager.speed,
                "heading": self.flight_manager.heading,
                "phase": self.flight_manager.phase,
                "onGround": self.flight_manager.on_ground
            }
        
        # If no flight started, just return raw connection status/data from provider
        if self.current_provider:
             return self.current_provider.get_raw_telemetry()
             
        return None

    def stop_tracking(self):
        """Stops the current provider to freeze telemetry."""
        if self.current_provider:
             self.current_provider.stop()
        
    def submit_pirep(self):
        """Submits the PIREP using the current flight manager."""
        if self.flight_manager:
            return self.flight_manager.submit_pirep()
        return False
