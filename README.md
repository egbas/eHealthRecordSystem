# eHealthRecordSystem — HI 741 Final Project

A role-based Tkinter desktop application for managing patient and hospital data, including
credential-based login, patient CRUD operations, clinical note viewing, admin access and management
analytics.

---

## Quick Start

### 1. Setting up environment and running program

For starters running the program, it's expected that python and git are already installed.
--- 
    clone the repo: `git clone https://github.com/egbas/eHealthRecordSystem.git`
    move to where repo is stored using `cd directoryname`
    create a virtual environment: `python -m venv venv`
    activate virtual environment: `venv\Scripts\Activate`
    run program: `python main.py`
---

### 2. Make sure the Data folder is populated

The `data/` directory should contain:
- `credentials.csv`
- `patients.csv`
- `providers.csv`
- `departments.csv`
- `encounters.csv`
- `procedures.csv`
- `notes.csv`



---

## Test Credentials

| Username | Password  | Role        |
|----------|-----------|-------------|
| alice    | pass123   | clinician   |
| brandon  | pass124   | clinician   |
| carmen   | pass125   | clinician   |
| nina     | pass201   | nurse       |
| omar     | pass202   | nurse       |
| paige    | pass203   | nurse       |
| dave     | pass000   | admin       |
| erin     | admin456  | admin       |
| frank    | admin789  | admin       |
| carol    | pass789   | management  |
| mia      | mgmt456   | management  |
| sam      | mgmt789   | management  |

---

## Role Permissions

| Role       | Available Actions |
|------------|-------------------|
| clinician  | Retrieve Patient, Add Patient, Remove Patient, Count Visits, View Note|
| nurse      | Same as clinician |
| admin      | Count Visits, Provider Workload |
| management | Department Revenue, Key Statistics |

---

## Project Structure


eHealthRecordSystem/
├── main.py                  # Entry point — run this file
├── requirements.txt
├── README.md
├── data/                    # Input CSV files
│   ├── credentials.csv
│   ├── patients.csv
│   ├── providers.csv
│   ├── departments.csv
│   ├── encounters.csv
│   ├── procedures.csv
│   └── notes.csv
├── output/                  # Generated output file is stored 
│   └── usage_statistics.csv
├── uml/
│   └── uml_diagram.png      # UML class diagram
└── src/
    ├── __init__.py
    ├── ehrs_ui.py               # Tkinter UI — App, LoginFrame, MenuFrame, action frames
    ├── patient.py           # Patient model + CRUD helpers
    ├── user.py              # User model + credential validation
    ├── patient_note.py              # Note model + lookup helpers
    ├── app_statistics.py        # Analytics: revenue, workload, key stats, encounter counts
    └── logger.py            # Usage statistics logger



## Output Files

| File | Description |
|------|-------------|
| `output/usage_statistics.csv` | Login events (successful and failed), actions performed, timestamps |
| `data/patients.csv` | Updated automatically when patients are added or removed |

---

## Dependencies

- Python 3.14.5
- `tkinter` (bundled with standard Python)
- No third-party packages required

---

## Notes for Programmers

- All data access goes through the helper functions in `patient.py`, `patient_note.py`, and `app_statistics.py`.
- The `App` class in `ehrs_ui.py` is the main controller; it owns the session state (`current_user`, `patients`, `encounters`, `notes`).
- Each action screen is a separate `_ActionFrame` subclass for easy extension.
- Usage logging happens automatically in every action frame via `self._log(...)`.
- If a user fails to log in, the failed attempt is still logged to `usage_statistics.csv` including all user actions.

---

## Version Control

GitHub repository: `https://github.com/egbas/eHealthRecordSystem.git`

Commit history demonstrates incremental development — see commit log for details.