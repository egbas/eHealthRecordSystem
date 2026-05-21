import csv
import os


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CREDENTIALS_FILE = os.path.join(DATA_DIR, "credentials.csv")

# Role constants
ROLE_CLINICIAN = "clinician"
ROLE_NURSE = "nurse"
ROLE_ADMIN = "admin"
ROLE_MANAGEMENT = "management"

ROLE_PERMISSIONS = {
    ROLE_CLINICIAN: [
        "retrieve_patient",
        "add_patient",
        "remove_patient",
        "count_visits",
        "view_note"
    ],
    ROLE_NURSE: [
        "retrieve_patient",
        "add_patient",
        "remove_patient",
        "count_visits",
        "view_note"
    ],
    ROLE_ADMIN: [
        "count_visits",
        "count_encounters_per_patient",
        "count_encounters_by_department",
        "monitor_workload",
    ],
    ROLE_MANAGEMENT: [
        "monitor_revenue",
        "generate_key_statistics",
    ],
}

class User:

    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role

    def has_permission(self, action: str) -> bool:
        return action in ROLE_PERMISSIONS.get(self.role, [])

    def get_menu_actions(self) -> list:
        return list(ROLE_PERMISSIONS.get(self.role, []))

    def __repr__(self):
        return f"User(username={self.username!r}, role={self.role!r})"



def load_credentials() -> dict:
    credentials = {}
    if not os.path.exists(CREDENTIALS_FILE):
        return credentials
    with open(CREDENTIALS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            credentials[row["username"]] = (row["password"], row["role"])
    return credentials


def login(username: str, password: str) -> tuple:
    
    credentials = load_credentials()
    if username not in credentials:
        return False, "Invalid username or password."
    stored_password, role = credentials[username]
    if stored_password != password:
        return False, "Invalid username or password."
    return True, User(username=username, role=role)