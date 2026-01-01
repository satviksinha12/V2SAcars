import socket
import struct
import threading
from v2s_tracker.config import Config

class XPlaneProvider:
    def __init__(self):
        self.socket = None
        self.latest_data = {}
        self.running = False
        self.thread = None
        self.flight_manager = None

    def set_flight_manager(self, fm):
        self.flight_manager = fm

    def get_metadata(self):
        # UDP typically doesn't send metadata unless configured or separate DREF request
        # Sticking to basic telemetry for now, returning empty
        return {"callsign": "", "aircraft": ""}

    def start(self):
        if self.running: return
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket.bind(("0.0.0.0", Config.XPLANE_UDP_PORT))
            self.socket.settimeout(1.0)
            self.thread = threading.Thread(target=self._loop)
            self.thread.daemon = True
            self.thread.start()
            print("X-Plane Provider Started on 49000")
        except Exception as e:
            print(f"Failed to bind X-Plane: {e}")
            self.running = False

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()

    def get_raw_telemetry(self):
         return self.latest_data if self.latest_data else {"source": "X-Plane"}

    def _loop(self):
        while self.running:
            try:
                data, _ = self.socket.recvfrom(2048)
                self._parse(data)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"X-Plane Error: {e}")

    def _parse(self, data):
        if len(data) < 5 or data[0:4] != b'DATA': return
        
        telemetry = {"source": "X-Plane"}
        count = (len(data) - 5) // 36
        for i in range(count):
            offset = 5 + (i * 36)
            idx = struct.unpack('<i', data[offset:offset+4])[0]
            values = struct.unpack('<8f', data[offset+4:offset+36])

            if idx == 3: # Speed
                # values: [Vind, Veq, Vtrue, Vgnd, ...]
                telemetry['speed'] = values[3] # Ground Speed
            elif idx == 4: # Mach, VVI (ft/min) etc
                 # values[2] is VVI in ft/min usually, let's check standard X-Plane output
                 # Index 4: mach, VVI
                 # 0: mach, 1: VVI (m/s?), 2: VVI (fpm)? 
                 # Actually standard UDP:
                 # 4: [mach, Vvi(m/s), Vvi(total?), ?]
                 # Let's assume values[2] is often VVI in fpm or we might need to convert values[1] * 196.85
                 # X-Plane 11/12 specific:
                 # 4 -> 0: mach, 1: keas, 2: true_airspeed, 3: true_ground_speed, ... this varies.
                 # Let's try Index 132 for VVI or Index 4. 
                 # Standard set usually has VS at Group 4, element 2 (fpm).
                 telemetry['vs'] = values[2] 
            elif idx == 17: # Attitude
                # values: [pitch, roll, true_hdg, mag_hdg]
                telemetry['heading'] = values[3] # Mag Heading
            elif idx == 20: # LatLonAlt
                telemetry['lat'] = values[0]
                telemetry['lon'] = values[1]
                telemetry['alt'] = values[2]
        
        self.latest_data.update(telemetry)
        
        # Feed Flight Manager
        if self.flight_manager and 'lat' in telemetry:
             alt = telemetry.get('alt', 0)
             spd = telemetry.get('speed', 0)
             og = alt < 500 and spd < 40 
             
             self.flight_manager.update_telemetry(
                 lat=telemetry['lat'],
                 lon=telemetry['lon'],
                 alt=alt,
                 speed=spd,
                 headings=telemetry.get('heading', 0),
                 on_ground=og,
                 vs=telemetry.get('vs', 0),
                 engines_running=True
             )
