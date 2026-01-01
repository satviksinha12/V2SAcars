import json
import os

SETTINGS_FILE = "settings.json"

class SettingsManager:
    @staticmethod
    def load():
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    @staticmethod
    def save(data):
        current = SettingsManager.load()
        current.update(data)
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(current, f)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    @staticmethod
    def get(key, default=None):
        data = SettingsManager.load()
        return data.get(key, default)

    @staticmethod
    def set(key, value):
        SettingsManager.save({key: value})
