from flask import Flask, render_template, request, jsonify, redirect
import json
import uuid

# WAJIB ADA DI ATAS
app = Flask(__name__)

# ======================
# DATA HANDLER
# ======================
def load_data():
    with open("data.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

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



