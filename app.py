from flask import Flask, render_template, request, redirect, session
import gspread
from google.oauth2.service_account import Credentials
import os, json, uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret")

# ======================
# LOGIN CONFIG
# ======================
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

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

CREDS = Credentials.from_service_account_info(
    json.loads(creds_json),
    scopes=SCOPE
)

gc = gspread.authorize(CREDS)
SHEET_ID = "1IhMywVAdRc7LfNMjspIYWKSwgAZ9-0RqLJWrT8zHqr8"
sheet = gc.open_by_key(SHEET_ID).sheet1

# ======================
# DATA HANDLER
# ======================
def load_data():
    try:
        return sheet.get_all_records()
    except:
        return []

def save_data(data):
    sheet.clear()
    sheet.append_row(["id","jenis","maskapai","kota","jam","status"])
    for d in data:
        sheet.append_row([
            d.get("id",""),
            d.get("jenis",""),
            d.get("maskapai",""),
            d.get("kota",""),
            d.get("jam",""),
            d.get("status","")
        ])

# ======================
# AUTH GUARD
# ======================
def login_required():
    return session.get("admin_logged_in") is True

# ======================
# LOGIN
# ======================
@app.route("/login", methods=["GET","POST"])
def login():
    error = ""
    if request.method == "POST":
        if (
            request.form["username"] == ADMIN_USERNAME and
            request.form["password"] == ADMIN_PASSWORD
        ):
            session["admin_logged_in"] = True
            return redirect("/admin")
        else:
            error = "Username atau password salah"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ======================
# FIDS
# ======================
@app.route("/", methods=["GET","HEAD"])
def index():
    if request.method == "HEAD":
        return "", 200

    data = load_data()
    keberangkatan = []
    kedatangan = []

    for d in data:
        if d.get("jenis","").lower() == "keberangkatan":
            keberangkatan.append(d)
        elif d.get("jenis","").lower() == "kedatangan":
            kedatangan.append(d)

    return render_template(
        "index.html",
        keberangkatan=keberangkatan,
        kedatangan=kedatangan
    )

# ======================
# ADMIN (PROTECTED)
# ======================
@app.route("/admin")
def admin():
    if not login_required():
        return redirect("/login")
    return render_template("admin.html", flights=load_data())

@app.route("/add", methods=["POST"])
def add():
    if not login_required():
        return redirect("/login")

    jam_baru = f"{request.form['jam']}:{request.form['menit']}"

    data = load_data()
    data.append({
        "id": str(uuid.uuid4()),
        "jenis": request.form["jenis"],
        "maskapai": request.form["maskapai"],
        "kota": request.form["kota"],
        "jam": jam_baru,
        "status": request.form["status"]
    })
    save_data(data)
    return redirect("/admin")


@app.route("/delete/<id>")
def delete(id):
    if not login_required():
        return redirect("/login")

    data = [d for d in load_data() if d.get("id") != id]
    save_data(data)
    return redirect("/admin")

@app.route("/update_status", methods=["POST"])
def update_status():
    if not login_required():
        return redirect("/login")

    data = load_data()
    for d in data:
        if d.get("id") == request.form["id"]:
            d["status"] = request.form["status"]
            break
    save_data(data)
    return redirect("/admin")

@app.route("/update_jam", methods=["POST"])
def update_jam():
    if not login_required():
        return redirect("/login")

    jam_baru = f"{request.form['jam_jam']}:{request.form['jam_menit']}"
    data = load_data()
    for d in data:
        if d.get("id") == request.form["id"]:
            d["jam"] = jam_baru
            break
    save_data(data)
    return redirect("/admin")

if __name__ == "__main__":
    app.run()

