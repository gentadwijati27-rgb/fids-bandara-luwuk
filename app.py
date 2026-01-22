from flask import Flask, render_template, request, jsonify, redirect
import gspread
from google.oauth2.service_account import Credentials

# WAJIB ADA DI ATAS
app = Flask(__name__)

# ======================
# GOOGLE SHEET SETUP
# ======================
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPE
)

gc = gspread.authorize(CREDS)
SHEET_ID = "PASTE_ID_SHEET_KAMU_DI_SINI"
sheet = gc.open_by_key(SHEET_ID).sheet1


def load_data():
    records = sheet.get_all_records()
    return records


def save_data(data):
    sheet.clear()
    sheet.append_row(["id", "jenis", "maskapai", "kota", "jam", "status"])
    for d in data:
        sheet.append_row([
            d["id"],
            d["jenis"],
            d["maskapai"],
            d["kota"],
            d["jam"],
            d["status"]
        ])

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




