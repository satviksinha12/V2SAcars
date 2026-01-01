import os

class Config:
    APP_NAME = "V2S Virtual Alliance ACARS"
    VERSION = "2.0.0" # Major version bump for Python rewrite
    API_BASE_URL = "https://v2svirtualalliance.web.app/api"
    
    # Colors (V2S Branding - Slate/Blue)
    COLOR_BG = "#0f172a"          # slate-900
    COLOR_FG = "#1e293b"          # slate-800
    COLOR_ACCENT = "#2563eb"      # blue-600
    COLOR_ACCENT_HOVER = "#1d4ed8" # blue-700
    COLOR_TEXT = "#f8fafc"        # slate-50
    COLOR_TEXT_DIM = "#94a3b8"    # slate-400
    COLOR_ERROR = "#ef4444"       # red-500
    COLOR_SUCCESS = "#22c55e"     # green-500

    # Simulator Settings
    XPLANE_UDP_PORT = 49000
    ACARS_INTERVAL_MS = 5000
