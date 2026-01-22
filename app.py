from flask import Flask, render_template, request, jsonify, redirect
import gspread
from google.oauth2.service_account import Credentials
import os
import json

# WAJIB ADA DI ATAS
app = Flask(__name__)

# ======================
# GOOGLE SHEET SETUP
# ======================
import os
import json
import gspread
from google.oauth2.service_account import Credentials

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

SHEET_ID = "1IhMywVAdRc7LfNMjspIYWKSwgAZ9-0RqLJWrT8zHqr8"
sheet = gc.open_by_key(SHEET_ID).sheet1




# ======================
# HALAMAN UTAMA (FIDS)
# ======================
@app.route("/")
def index():
    data = load_data()
    print("ISI DATA.JSON:", data)

    keberangkatan = [d for d in data if d.get("jenis") == "keberangkatan"]
    kedatangan = [d for d in data if d.get("jenis") == "kedatangan"]

    print("KEBERANGKATAN:", keberangkatan)
    print("KEDATANGAN:", kedatangan)

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
        "jam": request.form["jam"],
        "status": request.form["status"]
    })
    save_data(data)
    return redirect("/admin")

@app.route("/delete/<id>")
def delete(id):
    data = [d for d in load_data() if d["id"] != id]
    save_data(data)
    return redirect("/admin")

@app.route("/update_status", methods=["POST"])
def update_status():
    id_flight = request.form["id"]
    status_baru = request.form["status"]

    data = load_data()
    for d in data:
        if d["id"] == id_flight:
            d["status"] = status_baru
            break

    save_data(data)
    return redirect("/admin")

@app.route("/update_jam", methods=["POST"])
def update_jam():
    id_flight = request.form["id"]
    jam = request.form["jam_jam"]
    menit = request.form["jam_menit"]

    jam_baru = f"{jam}:{menit}"

    data = load_data()
    for d in data:
        if d["id"] == id_flight:
            d["jam"] = jam_baru
            break

    save_data(data)
    return redirect("/admin")

# ======================
# JALANKAN SERVER
# ======================
if __name__ == "__main__":
    app.run()

print("ENV GOOGLE_CREDENTIALS_JSON:", bool(os.environ.get("GOOGLE_CREDENTIALS_JSON")))







