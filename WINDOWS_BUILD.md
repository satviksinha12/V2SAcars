# Building V2S Tracker on Windows

Since this is a Python application with native UI dependencies (`customtkinter`), it is best built on a native Windows environment.

## Prerequisites
1.  **Python 3.10+** installed.
2.  **Git** installed.

## Build Steps

1.  **Open PowerShell** or Command Prompt.
2.  **Navigate** to the project folder.
3.  **Create a Virtual Environment** (Recommended):
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
4.  **Install Dependencies**:
    ```powershell
    pip install -r requirements.txt
    pip install pyinstaller
    ```
5.  **Build Code**:
    ```powershell
    pyinstaller v2s_tracker.spec --clean --noconfirm
    ```

## Output
The Windows executable (`V2S_ACARS.exe`) will be located in the `dist` folder.
