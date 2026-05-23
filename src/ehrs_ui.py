import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from src.user import login
from src.patient import (
    load_patients, load_encounters,
    add_patient, remove_patient, retrieve_patient,
    count_visits_on_date, count_visits_per_patient_on_date,
    count_visits_by_department_on_date,
)
from src.patient_note import load_notes, get_notes_for_patient_on_date
from src.app_statistics import (
    generate_key_statistics, monitor_revenue,
    monitor_workload,
)
from src import logger


BG       = "white"
FG       = "black"
FONT     = ("Courier New", 11)
FONT_B   = ("Courier New", 11, "bold")
FONT_LG  = ("Courier New", 13, "bold")


def _lbl(parent, text, font=FONT, **kw):
    return tk.Label(parent, text=text, bg=BG, fg=FG, font=font, **kw)

def _entry(parent, show=None, width=30):
    return tk.Entry(parent, bg="white", fg="black", font=FONT,
                    relief="solid", bd=1, width=width, show=show,
                    insertbackground="black")

def _btn(parent, text, command, width=20):
    return tk.Button(parent, text=text, command=command,
                     bg="white", fg="black", font=FONT,
                     relief="solid", bd=1, width=width,
                     activebackground="black", activeforeground="white",
                     cursor="hand2")

def _separator(parent):
    tk.Label(parent, text="-" * 60, bg=BG, fg=FG, font=FONT).pack(anchor="w")


class App(tk.Tk):
    """Main application window — manages session state and frame navigation."""

    def __init__(self):
        super().__init__()
        self.title("eHealth Record System")
        self.geometry("800x600")
        self.resizable(True, True)
        self.configure(bg=BG)

        self.current_user = None
        self.patients = {}
        self.encounters = []
        self.notes = []

        self._container = tk.Frame(self, bg=BG)
        self._container.pack(fill="both", expand=True, padx=20, pady=20)

        self._show_login()

    def _clear(self):
        for w in self._container.winfo_children():
            w.destroy()

    def _show_login(self):
        self._clear()
        LoginFrame(self._container, self).pack(fill="both", expand=True)

    def _show_menu(self):
        self._clear()
        MenuFrame(self._container, self).pack(fill="both", expand=True)

    def _show_frame(self, frame_cls):
        self._clear()
        frame_cls(self._container, self).pack(fill="both", expand=True)

    def login(self, username, password):
        success, result = login(username, password)
        if success:
            self.current_user = result
            self.patients = load_patients()
            self.encounters = load_encounters()
            self.notes = load_notes()
            logger.log_login(username, result.role, success=True)
            self._show_menu()
        else:
            logger.log_login(username, success=False)
            messagebox.showerror("Login Failed", result)

    def logout(self):
        if self.current_user:
            logger.log_logout(self.current_user.username, self.current_user.role)
        self.current_user = None
        self._show_login()

class LoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app

        _lbl(self, "=" * 40, FONT_B).pack(anchor="w", pady=(10, 0))
        _lbl(self, "  eHealth Record System", FONT_LG).pack(anchor="w")
        _lbl(self, "=" * 40, FONT_B).pack(anchor="w", pady=(0, 20))

        _lbl(self, "Username:").pack(anchor="w")
        self._username = _entry(self, width=30)
        self._username.pack(anchor="w", pady=(2, 10))
        self._username.focus()

        _lbl(self, "Password:").pack(anchor="w")
        self._password = _entry(self, show="*", width=30)
        self._password.pack(anchor="w", pady=(2, 16))
        self._password.bind("<Return>", lambda _: self._do_login())

        _btn(self, "[  LOGIN  ]", self._do_login, width=16).pack(anchor="w")

    def _do_login(self):
        u = self._username.get().strip()
        p = self._password.get().strip()
        if not u or not p:
            messagebox.showwarning("Input Error", "Username and password are required.")
            return
        self.app.login(u, p)


_ACTION_LABELS = {
    "retrieve_patient":               "1. Retrieve Patient",
    "add_patient":                    "2. Add Patient",
    "remove_patient":                 "3. Remove Patient",
    "count_visits":                   "4. Count Visits",
    "view_note":                      "5. View Clinical Note",
    "generate_key_statistics":        "6. Generate Key Statistics",
    "monitor_revenue":                "7. Department Revenue",
    "monitor_workload":               "8. Provider Workload",
}

_FRAME_MAP = {}   # filled after class definitions

class MenuFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        user = app.current_user

        _lbl(self, "=" * 40, FONT_B).pack(anchor="w")
        _lbl(self, "  MAIN MENU", FONT_LG).pack(anchor="w")
        _lbl(self, f"  Logged in as: {user.username}  [{user.role}]", FONT).pack(anchor="w")
        _lbl(self, "=" * 40, FONT_B).pack(anchor="w", pady=(0, 12))

        for action in user.get_menu_actions():
            label = _ACTION_LABELS.get(action, action)
            cmd = self._make_cmd(action)
            _btn(self, label, cmd, width=36).pack(anchor="w", pady=2)

        tk.Frame(self, bg=BG, height=10).pack()
        _btn(self, "[ LOGOUT ]", app.logout, width=14).pack(anchor="w", pady=(8, 0))

    def _make_cmd(self, action):
        frame_map = {
            "retrieve_patient":               RetrievePatientFrame,
            "add_patient":                    AddPatientFrame,
            "remove_patient":                 RemovePatientFrame,
            "count_visits":                   CountVisitsFrame,
            "view_note":                      ViewNoteFrame,
            "generate_key_statistics":        KeyStatisticsFrame,
            "monitor_revenue":                RevenueFrame,
            "monitor_workload":               WorkloadFrame,
        }
        def cmd():
            cls = frame_map.get(action)
            if cls:
                self.app._show_frame(cls)
        return cmd

class _ActionFrame(tk.Frame):
    title_text = "Action"

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app

        _lbl(self, "=" * 40, FONT_B).pack(anchor="w")
        _lbl(self, f"  {self.title_text}", FONT_LG).pack(anchor="w")
        _lbl(self, "=" * 40, FONT_B).pack(anchor="w", pady=(0, 10))

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(fill="both", expand=True)

        _btn(self, "[ BACK TO MENU ]", app._show_menu, width=18).pack(anchor="w", pady=(12, 0))

    def _result_box(self, parent=None):
        p = parent or self.content
        box = scrolledtext.ScrolledText(
            p, bg="white", fg="black", font=("Courier New", 10),
            relief="solid", bd=1, wrap="word", height=14,
            insertbackground="black"
        )
        box.pack(fill="both", expand=True, pady=(8, 0))
        return box

    def _show_result(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", text)
        box.configure(state="disabled")

    def _log(self, action, details=""):
        u = self.app.current_user
        logger.log_action(u.username, u.role, action, details)

class RetrievePatientFrame(_ActionFrame):
    title_text = "RETRIEVE PATIENT"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        c = self.content
        _lbl(c, "Patient ID:").pack(anchor="w")
        self._pid = _entry(c, width=20)
        self._pid.pack(anchor="w", pady=(2, 8))
        self._pid.focus()
        self._pid.bind("<Return>", lambda _: self._search())
        _btn(c, "[ SEARCH ]", self._search, width=12).pack(anchor="w")
        self._box = self._result_box()

    def _search(self):
        pid = self._pid.get().strip()
        if not pid:
            messagebox.showwarning("Input Error", "Please enter a Patient ID.")
            return
        ok, msg = retrieve_patient(self.app.patients, pid, self.app.encounters)
        self._show_result(self._box, msg)
        self._log("retrieve_patient", f"patient_id={pid}")

class AddPatientFrame(_ActionFrame):
    title_text = "ADD PATIENT"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        c = self.content

        fields = [
            ("Patient ID  :", "patient_id"),
            ("Age         :", "age"),
            ("BMI         :", "bmi"),
            ("A1C         :", "a1c"),
            ("BP Systolic :", "bp_sys"),
            ("BP Diastolic:", "bp_dia"),
        ]
        self._entries = {}
        for label, key in fields:
            row = tk.Frame(c, bg=BG)
            row.pack(anchor="w", pady=1)
            _lbl(row, label, width=14, anchor="w").pack(side="left")
            e = _entry(row, width=18)
            e.pack(side="left", padx=(4, 0))
            self._entries[key] = e

        row = tk.Frame(c, bg=BG)
        row.pack(anchor="w", pady=1)
        _lbl(row, "Gender      :", width=14, anchor="w").pack(side="left")
        self._gender = ttk.Combobox(row, values=["Male", "Female", "Non-binary"],
                                    width=16, state="readonly", font=FONT)
        self._gender.set("Male")
        self._gender.pack(side="left", padx=(4, 0))

        row2 = tk.Frame(c, bg=BG)
        row2.pack(anchor="w", pady=1)
        _lbl(row2, "Smoking     :", width=14, anchor="w").pack(side="left")
        self._smoking = tk.BooleanVar(value=False)
        tk.Checkbutton(row2, variable=self._smoking, bg=BG, fg=FG,
                       activebackground=BG, selectcolor="white",
                       font=FONT).pack(side="left", padx=(4, 0))

        _btn(c, "[ SUBMIT ]", self._submit, width=12).pack(anchor="w", pady=(10, 0))
        self._status = _lbl(c, "")
        self._status.pack(anchor="w", pady=(6, 0))

    def _submit(self):
        data = {k: e.get().strip() for k, e in self._entries.items()}
        data["gender"] = self._gender.get()
        data["smoking"] = str(self._smoking.get())
        if not data.get("patient_id"):
            messagebox.showwarning("Input Error", "Patient ID is required.")
            return
        ok, msg = add_patient(self.app.patients, data)
        self._status.configure(text=msg)
        self._log("add_patient", f"patient_id={data['patient_id']}")


class RemovePatientFrame(_ActionFrame):
    title_text = "REMOVE PATIENT"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        c = self.content
        _lbl(c, "Patient ID:").pack(anchor="w")
        self._pid = _entry(c, width=20)
        self._pid.pack(anchor="w", pady=(2, 8))
        self._pid.focus()
        _btn(c, "[ REMOVE ]", self._confirm, width=12).pack(anchor="w")
        self._status = _lbl(c, "")
        self._status.pack(anchor="w", pady=(8, 0))

    def _confirm(self):
        pid = self._pid.get().strip()
        if not pid:
            messagebox.showwarning("Input Error", "Please enter a Patient ID.")
            return
        if pid not in self.app.patients:
            self._status.configure(text=f"ERROR: Patient '{pid}' not found.")
            return
        if not messagebox.askyesno("Confirm", f"Remove all records for '{pid}'?"):
            return
        ok, msg = remove_patient(self.app.patients, pid)
        self._status.configure(text=msg)
        self._log("remove_patient", f"patient_id={pid}")


class CountVisitsFrame(_ActionFrame):
    title_text = "COUNT VISITS"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        c = self.content
        _lbl(c, "Date (YYYY-MM-DD):").pack(anchor="w")
        self._date = _entry(c, width=16)
        self._date.pack(anchor="w", pady=(2, 8))
        self._date.focus()

        _lbl(c, "Count by:").pack(anchor="w", pady=(4, 2))
        self._mode = tk.StringVar(value="total")
        for txt, val in [("Total visits", "total"),
                         ("Per patient", "per_patient"),
                         ("By department", "by_department")]:
            tk.Radiobutton(c, text=txt, variable=self._mode, value=val,
                           bg=BG, fg=FG, selectcolor="white",
                           activebackground=BG, font=FONT).pack(anchor="w")

        _btn(c, "[ COUNT ]", self._count, width=12).pack(anchor="w", pady=(10, 0))
        self._box = self._result_box()

    def _count(self):
        date = self._date.get().strip()
        if not date:
            messagebox.showwarning("Input Error", "Please enter a date.")
            return
        mode = self._mode.get()
        encs = self.app.encounters
        if mode == "total":
            result = f"Total visits on {date}: {count_visits_on_date(encs, date)}"
        elif mode == "per_patient":
            counts = count_visits_per_patient_on_date(encs, date)
            lines = [f"Visits per patient on {date}:", "=" * 36]
            lines += [f"  {pid}: {cnt}" for pid, cnt in sorted(counts.items())] or ["  No visits found."]
            result = "\n".join(lines)
        else:
            counts = count_visits_by_department_on_date(encs, date)
            lines = [f"Visits by department on {date}:", "=" * 36]
            lines += [f"  {did}: {cnt}" for did, cnt in sorted(counts.items())] or ["  No visits found."]
            result = "\n".join(lines)
        self._show_result(self._box, result)
        self._log("count_visits", f"date={date}, mode={mode}")

class ViewNoteFrame(_ActionFrame):
    title_text = "VIEW CLINICAL NOTE"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        c = self.content

        row = tk.Frame(c, bg=BG)
        row.pack(anchor="w")
        _lbl(row, "Patient ID:").pack(side="left")
        self._pid = _entry(row, width=14)
        self._pid.pack(side="left", padx=(4, 16))
        self._pid.focus()
        _lbl(row, "Date (YYYY-MM-DD):").pack(side="left")
        self._date = _entry(row, width=14)
        self._date.pack(side="left", padx=(4, 0))

        _btn(c, "[ VIEW NOTE ]", self._view, width=14).pack(anchor="w", pady=(10, 0))
        self._box = self._result_box()

    def _view(self):
        pid = self._pid.get().strip()
        date = self._date.get().strip()
        if not pid or not date:
            messagebox.showwarning("Input Error", "Enter both Patient ID and Date.")
            return
        notes = get_notes_for_patient_on_date(self.app.notes, pid, date)
        if not notes:
            self._show_result(self._box, f"No notes found for '{pid}' on {date}.")
        else:
            self._show_result(self._box, ("\n" + "-"*50 + "\n").join(n.display_string() for n in notes))
        self._log("view_note", f"patient_id={pid}, date={date}")

class KeyStatisticsFrame(_ActionFrame):
    title_text = "KEY STATISTICS"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        _btn(self.content, "[ GENERATE ]", self._generate, width=14).pack(anchor="w")
        self._box = self._result_box()

    def _generate(self):
        self._show_result(self._box, generate_key_statistics(self.app.patients, self.app.encounters))
        self._log("generate_key_statistics")

class RevenueFrame(_ActionFrame):
    title_text = "DEPARTMENT REVENUE"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        _btn(self.content, "[ GENERATE ]", self._generate, width=14).pack(anchor="w")
        self._box = self._result_box()

    def _generate(self):
        self._show_result(self._box, monitor_revenue())
        self._log("monitor_revenue")

class WorkloadFrame(_ActionFrame):
    title_text = "PROVIDER WORKLOAD"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        _btn(self.content, "[ GENERATE ]", self._generate, width=14).pack(anchor="w")
        self._box = self._result_box()

    def _generate(self):
        self._show_result(self._box, monitor_workload())
        self._log("monitor_workload")