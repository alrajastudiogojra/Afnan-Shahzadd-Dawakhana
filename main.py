import os
import sys
import sqlite3
import tempfile
import webbrowser
from datetime import datetime, date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

APP_NAME = "Afnan Shahzad Dawakhana"
PHONE = "0333-7676293"
ADDRESS = "Near Mand Barfi Shop, Tehsil Office Road, Gojra"
DB_NAME = "afnan_dawakhana.db"

def app_data_dir():
    root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    path = os.path.join(root, "AfnanDawakhana")
    os.makedirs(path, exist_ok=True)
    return path

DB_PATH = os.path.join(app_data_dir(), DB_NAME)

def get_sunday_for(d):
    # Monday=0 ... Sunday=6; return the most recent Sunday (today if Sunday)
    return d - timedelta(days=(d.weekday() + 1) % 7)

def date_label():
    return date.today().strftime("%d %b %Y")

class DawakhanaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Afnan Shahzad Dawakhana - Patient & Token System")
        self.root.geometry("1040x720")
        self.root.minsize(900, 620)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.init_db()
        self.build_ui()
        self.refresh_records()

    def init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_week TEXT NOT NULL,
                token_no INTEGER NOT NULL,
                patient_name TEXT NOT NULL,
                mobile TEXT,
                address TEXT,
                disease TEXT,
                created_at TEXT NOT NULL
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_patient_name ON patients(patient_name)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_patient_mobile ON patients(mobile)")
        self.conn.commit()

    def build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        header = ttk.Frame(self.root, padding=(18, 14))
        header.pack(fill="x")
        ttk.Label(header, text=APP_NAME, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(header, text=f"{ADDRESS}   |   Every Sunday: 9:00 AM - 4:00 PM",
                  font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))

        main = ttk.Frame(self.root, padding=(18, 4, 18, 16))
        main.pack(fill="both", expand=True)

        form = ttk.LabelFrame(main, text="New Patient / Token", padding=12)
        form.pack(fill="x")

        self.name_var = tk.StringVar()
        self.mobile_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.disease_var = tk.StringVar()
        self.token_var = tk.StringVar(value=self.next_token_display())

        ttk.Label(form, text="Token Number").grid(row=0, column=0, sticky="w", padx=6, pady=5)
        token_label = ttk.Label(form, textvariable=self.token_var, font=("Segoe UI", 20, "bold"),
                                foreground="#111111")
        token_label.grid(row=1, column=0, sticky="w", padx=6, pady=(0, 8))

        ttk.Label(form, text="Patient Name *").grid(row=0, column=1, sticky="w", padx=6, pady=5)
        ttk.Entry(form, textvariable=self.name_var, width=28).grid(row=1, column=1, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(form, text="Mobile Number").grid(row=0, column=2, sticky="w", padx=6, pady=5)
        ttk.Entry(form, textvariable=self.mobile_var, width=20).grid(row=1, column=2, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(form, text="Patient Address").grid(row=2, column=0, sticky="w", padx=6, pady=5)
        ttk.Entry(form, textvariable=self.address_var).grid(row=3, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(form, text="Disease / Problem").grid(row=2, column=2, sticky="w", padx=6, pady=5)
        ttk.Entry(form, textvariable=self.disease_var).grid(row=3, column=2, sticky="ew", padx=6, pady=(0, 8))

        actions = ttk.Frame(form)
        actions.grid(row=4, column=0, columnspan=3, sticky="w", padx=6, pady=(4, 0))
        ttk.Button(actions, text="Save Patient", command=self.save_patient).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Save & Print Slip", command=lambda: self.save_patient(print_after=True)).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Clear Form", command=self.clear_form).pack(side="left")

        for col in range(3):
            form.columnconfigure(col, weight=1)

        search_frame = ttk.LabelFrame(main, text="Search Patient Records", padding=10)
        search_frame.pack(fill="x", pady=(14, 10))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        search_entry.bind("<Return>", lambda _e: self.refresh_records())
        ttk.Button(search_frame, text="Search", command=self.refresh_records).pack(side="left", padx=(0, 8))
        ttk.Button(search_frame, text="Show All", command=self.show_all).pack(side="left")

        records_frame = ttk.LabelFrame(main, text="Saved Patients", padding=8)
        records_frame.pack(fill="both", expand=True)
        cols = ("token", "name", "mobile", "address", "disease", "date")
        self.tree = ttk.Treeview(records_frame, columns=cols, show="headings", height=12)
        headings = {
            "token": "Token", "name": "Patient Name", "mobile": "Mobile",
            "address": "Address", "disease": "Disease / Problem", "date": "Date"
        }
        widths = {"token": 70, "name": 170, "mobile": 120, "address": 230, "disease": 170, "date": 100}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="w")
        yscroll = ttk.Scrollbar(records_frame, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(records_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        records_frame.rowconfigure(0, weight=1)
        records_frame.columnconfigure(0, weight=1)

        bottom = ttk.Frame(main)
        bottom.pack(fill="x", pady=(8, 0))
        ttk.Label(bottom, text=f"Contact: {PHONE}   |   Data saved locally on this computer",
                  font=("Segoe UI", 9)).pack(side="left")
        ttk.Button(bottom, text="Print Selected Slip", command=self.print_selected).pack(side="right")

    def current_week_key(self):
        return get_sunday_for(date.today()).isoformat()

    def next_token_display(self):
        try:
            week = get_sunday_for(date.today()).isoformat()
            row = self.conn.execute("SELECT COALESCE(MAX(token_no), 0) AS n FROM patients WHERE token_week=?", (week,)).fetchone()
            return f"{(row['n'] if row else 0) + 1:03d}"
        except Exception:
            return "001"

    def save_patient(self, print_after=False):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Patient Name Required", "Please enter the patient's name.")
            return
        week = self.current_week_key()
        row = self.conn.execute("SELECT COALESCE(MAX(token_no), 0) AS n FROM patients WHERE token_week=?", (week,)).fetchone()
        token_no = int(row["n"] or 0) + 1
        created = datetime.now().isoformat(timespec="seconds")
        values = (week, token_no, name, self.mobile_var.get().strip(),
                  self.address_var.get().strip(), self.disease_var.get().strip(), created)
        cur = self.conn.execute("""
            INSERT INTO patients (token_week, token_no, patient_name, mobile, address, disease, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, values)
        self.conn.commit()
        patient = self.conn.execute("SELECT * FROM patients WHERE id=?", (cur.lastrowid,)).fetchone()
        self.token_var.set(f"{token_no:03d}")
        self.refresh_records()
        if print_after:
            self.print_patient(patient)
        messagebox.showinfo("Saved", f"Patient saved successfully. Token number: {token_no:03d}")
        self.clear_form()

    def clear_form(self):
        self.name_var.set("")
        self.mobile_var.set("")
        self.address_var.set("")
        self.disease_var.set("")
        self.token_var.set(self.next_token_display())

    def show_all(self):
        self.search_var.set("")
        self.refresh_records()

    def refresh_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        q = self.search_var.get().strip()
        if q:
            like = f"%{q}%"
            rows = self.conn.execute("""
                SELECT * FROM patients
                WHERE patient_name LIKE ? OR mobile LIKE ?
                ORDER BY id DESC LIMIT 500
            """, (like, like)).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM patients ORDER BY id DESC LIMIT 500").fetchall()
        for r in rows:
            created = datetime.fromisoformat(r["created_at"]).strftime("%d-%b-%Y")
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                f"{r['token_no']:03d}", r["patient_name"], r["mobile"] or "",
                r["address"] or "", r["disease"] or "", created
            ))

    def print_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Patient", "Please select a patient record first.")
            return
        row = self.conn.execute("SELECT * FROM patients WHERE id=?", (int(selected[0]),)).fetchone()
        if row:
            self.print_patient(row)

    @staticmethod
    def esc(value):
        return (str(value or "").replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;"))

    def print_patient(self, p):
        token = f"{p['token_no']:03d}"
        dt = datetime.fromisoformat(p["created_at"]).strftime("%d %b %Y")
        html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Token {token}</title>
<style>
@page {{ size: 80mm auto; margin: 3mm; }}
* {{ box-sizing: border-box; }}
body {{ width: 74mm; margin: 0 auto; color: #000; font-family: Arial, sans-serif; }}
.center {{ text-align: center; }}
.name {{ font-size: 17pt; font-weight: 800; line-height: 1.05; }}
.addr {{ font-size: 8.5pt; margin-top: 2mm; }}
.line {{ border-top: 1px dashed #000; margin: 3mm 0; }}
.time {{ font-size: 10pt; font-weight: bold; }}
.tokenbox {{ border: 2px solid #000; border-radius: 3mm; text-align: center; padding: 2mm; margin: 3mm 0; }}
.tokenlabel {{ font-size: 13pt; font-weight: bold; }}
.token {{ font-size: 38pt; font-weight: 900; line-height: 1.0; }}
.row {{ margin: 3mm 0; font-size: 10pt; overflow-wrap: anywhere; }}
.label {{ font-weight: bold; }}
.value {{ border-bottom: 1px dotted #000; min-height: 5mm; padding: 1mm 0; }}
.footer {{ text-align: center; font-size: 9pt; margin-top: 3mm; }}
.phone {{ font-size: 13pt; font-weight: 900; }}
</style></head><body>
<div class="center name">{self.esc(APP_NAME)}</div>
<div class="center addr">{self.esc(ADDRESS)}</div>
<div class="line"></div>
<div class="center time">EVERY SUNDAY | 09:00 AM - 04:00 PM</div>
<div class="tokenbox"><div class="tokenlabel">TOKEN NO.</div><div class="token">{token}</div></div>
<div class="row"><div class="label">Patient Name</div><div class="value">{self.esc(p['patient_name'])}</div></div>
<div class="row"><div class="label">Mobile Number</div><div class="value">{self.esc(p['mobile'])}</div></div>
<div class="row"><div class="label">Address</div><div class="value">{self.esc(p['address'])}</div></div>
<div class="row"><div class="label">Disease / Problem</div><div class="value">{self.esc(p['disease'])}</div></div>
<div class="line"></div>
<div class="footer">For more info</div>
<div class="center phone">{PHONE}</div>
<div class="center" style="font-size:8pt;margin-top:2mm">{dt}</div>
<script>window.onload = function() {{ window.print(); }};</script>
</body></html>"""
        out = os.path.join(tempfile.gettempdir(), f"afnan_token_{token}.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        webbrowser.open("file:///" + out.replace("\\", "/"))

    def on_close(self):
        self.conn.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = DawakhanaApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
