import csv
import os
from collections import Counter


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data")
PROCEDURES_FILE = os.path.join(DATA_DIR, "procedures.csv")
ENCOUNTERS_FILE = os.path.join(DATA_DIR, "encounters.csv")
PROVIDERS_FILE = os.path.join(DATA_DIR, "providers.csv")
DEPARTMENTS_FILE = os.path.join(DATA_DIR, "departments.csv")


def load_csv(filepath: str) -> list:
    if not os.path.exists(filepath):
        return []
    with open(filepath, newline="") as f:
        return list(csv.DictReader(f))
    
def monitor_revenue() -> str:
    
    procedures = load_csv(PROCEDURES_FILE)
    encounters = load_csv(ENCOUNTERS_FILE)
    departments = load_csv(DEPARTMENTS_FILE)

    dept_names = {dept["department_id"]: dept["name"] for dept in departments}
    enc_dept = {enc["encounter_id"]: enc["department_id"] for enc in encounters}

    revenue = {}
    for proc in procedures:
        dept_id = enc_dept.get(proc["encounter_id"], "Unknown")
        try:
            cost = float(proc["cost"])
        except (ValueError, KeyError):
            cost = 0.0
        revenue[dept_id] = revenue.get(dept_id, 0.0) + cost

    lines = ["Department Revenue Report", "=" * 40]
    for dept_id, total in sorted(revenue.items(), key=lambda x: -x[1]):
        name = dept_names.get(dept_id, dept_id)
        lines.append(f"  {name} ({dept_id}): ${total:,.2f}")
    if not revenue:
        lines.append("  No data available.")
    return "\n".join(lines)


def monitor_workload() -> str:
    
    encounters = load_csv(ENCOUNTERS_FILE)
    providers = load_csv(PROVIDERS_FILE)

    prov_names = {provider["provider_id"]: provider["name"] for provider in providers}
    prov_specialty = {provider["provider_id"]: provider["specialty"] for provider in providers}

    counts = Counter(encounter["provider_id"] for encounter in encounters)

    lines = ["Provider Workload Report", "=" * 40]
    lines.append(f"{'Rank':<6}{'Provider':<12}{'Name':<16}{'Specialty':<22}{'Encounters'}")
    lines.append("-" * 70)
    for rank, (pid, cnt) in enumerate(counts.most_common(), start=1):
        name = prov_names.get(pid, "Unknown")
        specialty = prov_specialty.get(pid, "Unknown")
        lines.append(f"  {rank:<4}{pid:<12}{name:<16}{specialty:<22}{cnt}")
    if not counts:
        lines.append("  No data available.")
    return "\n".join(lines)


def count_encounters_per_patient(encounters: list) -> str:
   
    counts = Counter(encounter["patient_id"] for encounter in encounters)
    lines = ["Encounters Per Patient", "=" * 40]
    for pid, cnt in sorted(counts.items()):
        lines.append(f"  {pid}: {cnt} encounter(s)")
    if not counts:
        lines.append("  No data available.")
    return "\n".join(lines)


def count_encounters_by_department(encounters: list) -> str:
    
    departments = load_csv(DEPARTMENTS_FILE)
    dept_names = {dept["department_id"]: dept["name"] for dept in departments}

    counts = Counter(enc["department_id"] for enc in encounters)
    lines = ["Encounters By Department", "=" * 40]
    for did, cnt in sorted(counts.items()):
        name = dept_names.get(did, did)
        lines.append(f"  {name} ({did}): {cnt} encounter(s)")
    if not counts:
        lines.append("  No data available.")
    return "\n".join(lines)


def generate_key_statistics(patients: dict, encounters: list) -> str:
    
    if not patients:
        return "No patient data available."

    ages = []
    bmis = []
    a1cs = []
    genders = Counter()
    smoking_count = 0

    for p in patients.values():
        try:
            ages.append(float(p.age))
        except (ValueError, TypeError):
            pass
        try:
            bmis.append(float(p.bmi))
        except (ValueError, TypeError):
            pass
        if p.a1c != "":
            try:
                a1cs.append(float(p.a1c))
            except (ValueError, TypeError):
                pass
        genders[p.gender] += 1
        if str(p.smoking).lower() == "true":
            smoking_count += 1

    enc_types = Counter(enc["encounter_type"] for enc in encounters)
    dept_counts = Counter(enc["department_id"] for enc in encounters)

    def fmt(values):
        if not values:
            return "N/A"
        avg = sum(values) / len(values)
        return f"{avg:.2f} (min {min(values):.1f}, max {max(values):.1f})"

    lines = [
        "Key Statistics Report",
        "=" * 50,
        f"Total Patients        : {len(patients)}",
        f"Total Encounters      : {len(encounters)}",
        "",
        "Patient Demographics",
        "-" * 30,
        f"  Average Age         : {fmt(ages)}",
        f"  Average BMI         : {fmt(bmis)}",
        f"  Average A1C         : {fmt(a1cs)} (patients with data: {len(a1cs)})",
        f"  Smoking (Yes)       : {smoking_count} ({smoking_count/max(len(patients),1)*100:.1f}%)",
        "",
        "Gender Distribution",
        "-" * 30,
    ]
    for gender, cnt in genders.most_common():
        pct = cnt / max(len(patients), 1) * 100
        lines.append(f"  {gender:<18}: {cnt} ({pct:.1f}%)")

    lines += [
        "",
        "Encounter Types",
        "-" * 30,
    ]
    for etype, cnt in enc_types.most_common():
        lines.append(f"  {etype:<18}: {cnt}")

    lines += [
        "",
        "Encounters by Department",
        "-" * 30,
    ]
    for dept, cnt in dept_counts.most_common():
        lines.append(f"  {dept:<18}: {cnt}")

    return "\n".join(lines)