from flask import Flask, render_template, request, redirect
import gspread
from google.oauth2.service_account import Credentials
import os
import json
import uuid

# ======================
# APP INIT
# ======================
app = Flask(__name__)

# ======================
# GOOGLE SHEET SETUP
# ======================
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")

if not creds_json:
    raise Exception("GOOGLE_CREDENTIALS_JSON environment variable not set")

creds_dict = json.loads(creds_json)

CREDS = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPE
)

gc = gspread.authorize(CREDS)

# GANTI DENGAN ID GOOGLE SHEET KAMU
SHEET_ID = "1IhMywVAdRc7LfNMjspIYWKSwgAZ9-0RqLJWrT8zHqr8"
sheet = gc.open_by_key(SHEET_ID).sheet1

# ======================
# DATA HANDLER (AMAN)
# ======================
def load_data():
    try:
        records = sheet.get_all_records()
        if not isinstance(records, list):
            return []
        return records
    except Exception as e:
        print("ERROR LOAD DATA:", e)
        return []

def save_data(data):
    try:
        sheet.clear()
        sheet.append_row(["id", "jenis", "maskapai", "kota", "jam", "status"])
        for d in data:
            sheet.append_row([
                d.get("id", ""),
                d.get("jenis", ""),
                d.get("maskapai", ""),
                d.get("kota", ""),
                d.get("jam", ""),
                d.get("status", "")
            ])
    except Exception as e:
        print("ERROR SAVE DATA:", e)

# ======================
# HALAMAN UTAMA (FIDS)
# ======================
@app.route("/", methods=["GET", "HEAD"])
def index():
    # Penting untuk Render (health check)
    if request.method == "HEAD":
        return "", 200

    data = load_data()

    keberangkatan = []
    kedatangan = []

    for d in data:
        if not isinstance(d, dict):
            continue
        jenis = d.get("jenis", "").strip().lower()
        if jenis == "keberangkatan":
            keberangkatan.append(d)
        elif jenis == "kedatangan":
            kedatangan.append(d)

    return render_template(
        "index.html",
        keberangkatan=keberangkatan,
        kedatangan=kedatangan
    )

# ======================
# ADMIN
# ======================
@app.route("/admin")
def admin():
    return render_template("admin.html", flights=load_data())

@app.route("/add", methods=["POST"])
def add():
    data = load_data()
    data.append({
        "id": str(uuid.uuid4()),
        "jenis": request.form["jenis"],
        "maskapai": request.form["maskapai"],
        "kota": request.form["kota"],
        # JAM 24 JAM (00–23) + MENIT (00–59)
        "jam": f"{request.form['jam']}:{request.form['menit']}",
        "status": request.form["status"]
    })
    save_data(data)
    return redirect("/admin")

@app.route("/delete/<id>")
def delete(id):
    data = [d for d in load_data() if d.get("id") != id]
    save_data(data)
    return redirect("/admin")

@app.route("/update_status", methods=["POST"])
def update_status():
    data = load_data()
    for d in data:
        if d.get("id") == request.form["id"]:
            d["status"] = request.form["status"]
            break
    save_data(data)
    return redirect("/admin")

@app.route("/update_jam", methods=["POST"])
def update_jam():
    jam_baru = f"{request.form['jam_jam']}:{request.form['jam_menit']}"
    data = load_data()
    for d in data:
        if d.get("id") == request.form["id"]:
            d["jam"] = jam_baru
            break
    save_data(data)
    return redirect("/admin")

# ======================
# RUN LOCAL (AMAN UNTUK RENDER)
# ======================
if __name__ == "__main__":
    app.run()
