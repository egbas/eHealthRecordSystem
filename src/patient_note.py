import csv
import os


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
NOTES_FILE = os.path.join(DATA_DIR, "notes.csv")


class Note:

    FIELDNAMES = ["note_id", "patient_id", "encounter_id", "note_date", "note_type", "note_text"]

    def __init__(self, note_id, patient_id, encounter_id, note_date, note_type, note_text):
        self.note_id = note_id
        self.patient_id = patient_id
        self.encounter_id = encounter_id
        self.note_date = note_date
        self.note_type = note_type
        self.note_text = note_text

    @classmethod
    def from_dict(cls, row: dict) -> "Note":
        return cls(
            note_id=row["note_id"],
            patient_id=row["patient_id"],
            encounter_id=row["encounter_id"],
            note_date=row["note_date"],
            note_type=row["note_type"],
            note_text=row["note_text"],
        )

    def display_string(self) -> str:
        return (
            f"Note ID     : {self.note_id}\n"
            f"Patient ID  : {self.patient_id}\n"
            f"Encounter ID: {self.encounter_id}\n"
            f"Date        : {self.note_date}\n"
            f"Type        : {self.note_type}\n"
            f"\n{self.note_text}"
        )


def load_notes() -> list:
    notes = []
    if not os.path.exists(NOTES_FILE):
        return notes
    with open(NOTES_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            notes.append(Note.from_dict(row))
    return notes


def get_notes_for_patient_on_date(notes: list, patient_id: str, date_str: str) -> list:
    return [
        note for note in notes
        if note.patient_id == patient_id and note.note_date == date_str
    ]