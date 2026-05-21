import csv
import os
from datetime import datetime


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
USAGE_FILE = os.path.join(OUTPUT_DIR, "usage_statistics.csv")

FIELDNAMES = ["timestamp", "username", "role", "action", "status", "details"]


def log_directory():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def log_event(username: str, role: str, action: str, status: str = "success", details: str = "") -> None:
    log_directory()
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "role": role,
        "action": action,
        "status": status,
        "details": details,
    }
    with open(USAGE_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)


def log_login(username: str, role: str = "", success: bool = True) -> None:
    if success:
        log_event(username, role, action="login", status="success")
    else:
        log_event(username, role="unknown", action="login", status="failed_login_attempt")


def log_action(username: str, role: str, action: str, details: str = "") -> None:
    log_event(username, role, action=action, status="success", details=details)


def log_logout(username: str, role: str) -> None:
    log_event(username, role, action="logout", status="success")