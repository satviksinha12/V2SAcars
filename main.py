import customtkinter as ctk
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from v2s_tracker.ui.main_window import MainWindow

def main():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
