import requests
import math
import time
from v2s_tracker.config import Config

class FlightPhase:
    BOARDING = "Boarding"
    TAXI_OUT = "Taxi Out"
    TAKEOFF = "Takeoff"
    CLIMBING = "Climbing"
    CRUISE = "Cruise"
    DESCENDING = "Descending"
    APPROACH = "Approach"
    LANDING = "Landing"
    TAXI_IN = "Taxi In"
    PARKED = "Parked"

class FlightManager:
    def __init__(self, pilot_id, callsign, aircraft_type, dep, arr, cruise_alt):
        self.pilot_id = pilot_id
        self.callsign = callsign
        self.aircraft_type = aircraft_type
        self.dep = dep
        self.arr = arr
        self.cruise_alt = int(cruise_alt)
        self.phase = FlightPhase.BOARDING
        self.flight_id = f"{callsign}"
        
        self.max_alt = 0
        self.distance_flown = 0
        self.last_lat = None
        self.last_lon = None
        self.landing_rate = 0
        self.fuel_used = 0
        
        # Telemetry State
        self.lat = 0
        self.lon = 0
        self.alt = 0
        self.speed = 0
        self.heading = 0
        self.on_ground = True

    def update_telemetry(self, lat, lon, alt, speed, headings, on_ground, vs, engines_running):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.speed = speed
        self.heading = headings
        self.on_ground = on_ground

        self.update_phase(alt, speed, on_ground, vs, engines_running)
        self.calculate_distance(lat, lon)
        self.send_acars()

        if self.phase == FlightPhase.PARKED:
            # Trigger PIREP?
            pass

    def update_phase(self, alt, speed, on_ground, vertical_speed, engines_running):
        # Basic state machine ported from reference
        if self.phase == FlightPhase.BOARDING:
            if engines_running and speed > 5:
                self.phase = FlightPhase.TAXI_OUT
        
        elif self.phase == FlightPhase.TAXI_OUT:
            if not on_ground and alt > 100: 
                self.phase = FlightPhase.TAKEOFF
            elif speed > 40 and on_ground: # Fast taxi/takeoff roll
                self.phase = FlightPhase.TAKEOFF

        elif self.phase == FlightPhase.TAKEOFF:
            if alt > 1000 and vertical_speed > 100:
                self.phase = FlightPhase.CLIMBING
        
        elif self.phase == FlightPhase.CLIMBING:
            if (alt > self.cruise_alt - 1000) or (vertical_speed < 100 and vertical_speed > -100 and alt > 10000 and self.cruise_alt > 20000):
                self.phase = FlightPhase.CRUISE
        
        elif self.phase == FlightPhase.CRUISE:
            if vertical_speed < -200 and alt < self.cruise_alt - 500:
                self.phase = FlightPhase.DESCENDING
        
        elif self.phase == FlightPhase.DESCENDING:
            if alt < 3000:
                self.phase = FlightPhase.APPROACH

        elif self.phase == FlightPhase.APPROACH:
            if on_ground:
                self.phase = FlightPhase.LANDING
                self.landing_rate = vertical_speed
        
        elif self.phase == FlightPhase.LANDING:
            if speed < 30:
                self.phase = FlightPhase.TAXI_IN
        
        elif self.phase == FlightPhase.TAXI_IN:
            if not engines_running and speed < 5:
                self.phase = FlightPhase.PARKED

        return self.phase

    def calculate_distance(self, lat, lon):
        if self.last_lat is not None:
            R = 6371  # km
            dLat = math.radians(lat - self.last_lat)
            dLon = math.radians(lon - self.last_lon)
            a = math.sin(dLat/2) * math.sin(dLat/2) + \
                math.cos(math.radians(self.last_lat)) * math.cos(math.radians(lat)) * \
                math.sin(dLon/2) * math.sin(dLon/2)
            c = 2 * math.asin(math.sqrt(a))
            dist = R * c
            self.distance_flown += dist
        
        self.last_lat = lat
        self.last_lon = lon

    def send_acars(self):
        payload = {
            "pilotId": self.pilot_id,
            "flightId": self.flight_id,
            "callsign": self.callsign,
            "dep": self.dep,
            "arr": self.arr,
            "aircraft": self.aircraft_type,
            "lat": self.lat,
            "lon": self.lon,
            "alt": int(self.alt),
            "heading": int(self.heading),
            "speed": int(self.speed),
            "phase": self.phase
        }
        try:
            requests.post(f"{Config.API_BASE_URL}/acars", json=payload, timeout=2)
        except:
            pass

    def submit_pirep(self, fuel_used=0, duration_min=0):
        # Calculate duration if not provided
        payload = {
            "username": self.pilot_id,
            "flightId": self.flight_id,
            "dep": self.dep,
            "arr": self.arr,
            "aircraft": self.aircraft_type,
            "flightTime": f"{int(duration_min // 60)}:{int(duration_min % 60):02d}",
            "distance": int(self.distance_flown * 0.539957), # KM to NM
            "landingRate": int(self.landing_rate),
            "fuelUsed": int(fuel_used),
            "status": "Approved", 
            "proofType": "acars"
        }
        try:
            print(f"Submitting PIREP: {payload}")
            res = requests.post(f"{Config.API_BASE_URL}/pireps", json=payload)
            return res.status_code == 200
        except Exception as e:
            print(f"Error submitting PIREP: {e}")
            return False
