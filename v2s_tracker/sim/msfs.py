import platform
import threading
import time

try:
    from SimConnect import SimConnect, AircraftRequests
    NATIVE_SUPPORT = True
except ImportError:
    NATIVE_SUPPORT = False

class MsfsProvider:
    def __init__(self):
        self.sm = None
        self.aq = None
        self.running = False
        self.latest_data = {"source": "MSFS"}
        self.flight_manager = None
        self.meta_data = {}

    def set_flight_manager(self, fm):
        self.flight_manager = fm

    def get_metadata(self):
        # Allow UI to pull fetched metadata
        return self.meta_data

    def start(self):
        if platform.system() != "Windows":
             self.latest_data = {"source": "MSFS (Requires Windows)"}
             # Mock for Linux testing of Sync?
             # self.meta_data = {"callsign": "MOCK101", "aircraft": "Airbus A320"} 
             return 

        if not NATIVE_SUPPORT:
            return

        if self.running: return
        self.running = True
        threading.Thread(target=self._connect, daemon=True).start()

    def _connect(self):
        while self.running:
            try:
                if not self.sm:
                    try:
                        self.sm = SimConnect()
                        self.aq = AircraftRequests(self.sm, _time=200)
                        print("MSFS Connected")
                    except Exception as e:
                        time.sleep(2)
                        continue
                
                # Fetch Telemetry
                lat = self.aq.get("PLANE_LATITUDE")
                lon = self.aq.get("PLANE_LONGITUDE")
                alt = self.aq.get("PLANE_ALTITUDE")
                spd = self.aq.get("GROUND_VELOCITY") # Use Ground Speed for ACARS/Phase
                hdg = self.aq.get("PLANE_HEADING_DEGREES_MAGNETIC") # Use Mag Heading
                og = self.aq.get("SIM_ON_GROUND")
                vs = self.aq.get("VERTICAL_SPEED")
                eng = self.aq.get("GENERAL_ENG_COMBUSTION:1") 
                
                # Fetch Metadata (Periodic?)
                # Note: ATC ID might need occasional fetch not 5Hz
                callsign = self.aq.get("ATC_ID")
                title = self.aq.get("TITLE") 
                
                if callsign: self.meta_data["callsign"] = str(callsign)
                if title: self.meta_data["aircraft"] = str(title)

                if lat is not None:
                    self.latest_data = {
                        "source": "MSFS",
                        "lat": lat, "lon": lon, "alt": alt, 
                        "speed": spd, "heading": hdg, "onGround": og
                    }
                    
                    if self.flight_manager:
                        self.flight_manager.update_telemetry(
                            lat=lat, lon=lon, alt=alt, speed=spd, headings=hdg,
                            on_ground=bool(og), vs=vs, engines_running=bool(eng)
                        )

                time.sleep(0.2)
            except Exception as e:
                self.sm = None
                time.sleep(2)

    def stop(self):
        self.running = False
        if self.sm:
             try:
                 self.sm.quit()
             except: pass
             self.sm = None

    def get_raw_telemetry(self):
        return self.latest_data
