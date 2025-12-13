import os
import sys

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

DB_FOLDER = "managed_faces"
TOKEN_FILE = "tokens.txt"

# Global variable to store the Permanent API Key
_PERMANENT_API_KEY = None


def load_api_key():
    """Reads the Permanent API Key from the first line of the tokens.txt file"""
    global _PERMANENT_API_KEY
    if not os.path.exists(TOKEN_FILE):
        print(f"❌ Error: File {TOKEN_FILE} not found.")
        sys.exit(1)

    with open(TOKEN_FILE, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if not lines:
        print("❌ Error: tokens.txt file is empty!")
        sys.exit(1)

    # Use the first line as the Permanent API Key
    _PERMANENT_API_KEY = lines[0]
    print(f"✅ Loaded Permanent API Key: {_PERMANENT_API_KEY[:10]}...")


def get_current_token():
    """
    Returns the permanent API key.
    Luxand Cloud uses permanent keys, no token rotation needed.
    """
    if not _PERMANENT_API_KEY:
        load_api_key()
    return _PERMANENT_API_KEY


# Auto-create folder and load key upon import
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

load_api_key()  # Load Permanent API Key immediately upon script execution