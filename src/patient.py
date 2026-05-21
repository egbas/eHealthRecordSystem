import csv
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PATIENTS_FILE = os.path.join(DATA_DIR, "patients.csv")
ENCOUNTERS_FILE = os.path.join(DATA_DIR, "encounters.csv")

class Patient:

    FIELDNAMES = ["patient_id", "age", "gender", "bmi", "a1c", "bp_sys", "bp_dia", "smoking"]

    def __init__(self, patient_id, age, gender, bmi, a1c, bp_sys, bp_dia, smoking):
        self.patient_id = patient_id
        self.age = age
        self.gender = gender
        self.bmi = bmi
        self.a1c = a1c
        self.bp_sys = bp_sys
        self.bp_dia = bp_dia
        self.smoking = smoking

    @classmethod
    def from_dict(cls, row: dict) -> "Patient":
        return cls(
            patient_id=row["patient_id"],
            age=row["age"],
            gender=row["gender"],
            bmi=row["bmi"],
            a1c=row["a1c"],
            bp_sys=row["bp_sys"],
            bp_dia=row["bp_dia"],
            smoking=row["smoking"],
        )

    def to_dict(self) -> dict:
        return {
            "patient_id": self.patient_id,
            "age": self.age,
            "gender": self.gender,
            "bmi": self.bmi,
            "a1c": self.a1c,
            "bp_sys": self.bp_sys,
            "bp_dia": self.bp_dia,
            "smoking": self.smoking,
        }

    def display_string(self) -> str:
        a1c_display = self.a1c if self.a1c != "" else "N/A"
        smoking_display = "Yes" if str(self.smoking).lower() == "true" else "No"
        return (
            f"Patient ID  : {self.patient_id}\n"
            f"Age         : {self.age}\n"
            f"Gender      : {self.gender}\n"
            f"BMI         : {self.bmi}\n"
            f"A1C         : {a1c_display}\n"
            f"BP (Sys/Dia): {self.bp_sys} / {self.bp_dia}\n"
            f"Smoking     : {smoking_display}"
        )
    

def load_patients() -> dict:
    patients = {}
    if not os.path.exists(PATIENTS_FILE):
        return patients
    with open(PATIENTS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = Patient.from_dict(row)
            patients[p.patient_id] = p
    return patients


def save_patients(patients: dict) -> None:
    with open(PATIENTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=Patient.FIELDNAMES)
        writer.writeheader()
        for p in patients.values():
            writer.writerow(p.to_dict())


def add_patient(patients: dict, patient_data: dict) -> tuple:
    
    patient_id = patient_data.get("patient_id", "").strip()
    if not patient_id:
        return False, "Patient ID cannot be empty."

    patient = Patient(
        patient_id=patient_id,
        age=patient_data.get("age", ""),
        gender=patient_data.get("gender", ""),
        bmi=patient_data.get("bmi", ""),
        a1c=patient_data.get("a1c", ""),
        bp_sys=patient_data.get("bp_sys", ""),
        bp_dia=patient_data.get("bp_dia", ""),
        smoking=patient_data.get("smoking", ""),
    )
    existed = patient_id in patients
    patients[patient_id] = patient
    save_patients(patients)
    if existed:
        return True, f"Patient {patient_id} updated successfully."
    return True, f"Patient {patient_id} added successfully."


def remove_patient(patients: dict, patient_id: str) -> tuple:
    
    if patient_id not in patients:
        return False, f"Patient ID '{patient_id}' not found."
    del patients[patient_id]
    save_patients(patients)
    return True, f"Patient {patient_id} removed successfully."


def retrieve_patient(patients: dict, patient_id: str, encounters: list) -> tuple:
    
    if patient_id not in patients:
        return False, f"Patient ID '{patient_id}' not found."

    patient = patients[patient_id]

    patient_encounters = [e for e in encounters if e["patient_id"] == patient_id]
    result = patient.display_string()
    if patient_encounters:
        latest = max(patient_encounters, key=lambda e: e["encounter_date"])
        result += (
            f"\n\nMost Recent Visit\n"
            f"  Date       : {latest['encounter_date']}\n"
            f"  Type       : {latest['encounter_type']}\n"
            f"  Department : {latest['department_id']}"
        )
    return True, result


def load_encounters() -> list:
    encounters = []
    if not os.path.exists(ENCOUNTERS_FILE):
        return encounters
    with open(ENCOUNTERS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        encounters = list(reader)
    return encounters


def count_visits_on_date(encounters: list, date_str: str) -> int:
    return sum(1 for encounter in encounters if encounter["encounter_date"] == date_str)


def count_visits_per_patient_on_date(encounters: list, date_str: str) -> dict:
    
    counts = {}
    for encounter in encounters:
        if encounter["encounter_date"] == date_str:
            patient_id = encounter["patient_id"]
            counts[patient_id] = counts.get(patient_id , 0) + 1
    return counts


def count_visits_by_department_on_date(encounters: list, date_str: str) -> dict:
    
    counts = {}
    for encounter in encounters:
        if encounter["encounter_date"] == date_str:
            department_id = encounter["department_id"]
            counts[department_id] = counts.get(department_id, 0) + 1
    return counts
