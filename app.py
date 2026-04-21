import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"



import uuid
from flask import Flask, render_template, request, jsonify
from config import Config
from database import init_db, insert_complaint, fetch_counts, fetch_recent
from predictor import Predictor
from legal_mapping import LegalMapper
from flask import session
from gemini_chat import generate_reply



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "frontend"),
    static_folder=os.path.join(BASE_DIR, "..", "static")
)

app.config.from_object(Config)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")


os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

init_db()
predictor = Predictor()
mapper = LegalMapper()

# ----------------------
# PAGE ROUTES (Tabs)
# ----------------------
@app.route("/ping")
def ping():
    return "OK"
@app.route("/")
def home_page():
    return render_template("index.html", active="home")

@app.route("/detect")
def detect_page():
    return render_template("detect.html", active="detect")

@app.route("/report")
def report_page():
    return render_template("report.html", active="report")

@app.route("/legal")
def legal_page():
    return render_template("legal.html", active="legal")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html", active="dashboard")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()

    history = session.get("chat_history", [])
    try:
        reply, new_hist = generate_reply(msg, history, model="gemini-2.5-flash")
        session["chat_history"] = new_hist
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"⚠️ Chat error: {type(e).__name__}: {str(e)}"}), 200

# ----------------------
# API ROUTES
# ----------------------
@app.post("/api/detect")
def api_detect():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Text is required"}), 400

    pred = predictor.predict(text)

    legal_out = mapper.map_law(text, pred["toxic_score"], pred["threat_score"])

    #severity = mapper.severity_from_scores(pred["toxic_score"], pred["threat_score"])
    #legal = mapper.map_law(severity, pred["threat_score"], pred["toxic_score"])

    # return fields that your detect.js expects :contentReference[oaicite:3]{index=3}
    return jsonify({
        "label": pred["label"],
        "confidence": pred["confidence"],
        "severity": legal_out["severity"],
        "toxic_score": pred["toxic_score"],
        "threat_score": pred["threat_score"],
        "legal_mapping": legal_out,
        "legal_section": ",".join(legal_out.get("legal_sections",[])),
        "cleaned_text": pred["cleaned"]
    })


@app.post("/api/report")
def api_report():
    # form-data upload matches your report.js :contentReference[oaicite:4]{index=4}
    victim_name = (request.form.get("name") or "").strip()
    platform = (request.form.get("platform") or "").strip()
    bullying_text = (request.form.get("complaint") or "").strip()

    if not victim_name or not platform or not bullying_text:
        return jsonify({"error": "name, platform, complaint are required"}), 400

    # screenshot file (optional)
    screenshot_path = None
    file = request.files.get("screenshot")
    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        safe_name = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(Config.UPLOAD_FOLDER, safe_name)
        file.save(save_path)
        screenshot_path = f"uploads/{safe_name}"

    # run detection on reported text too
    pred = predictor.predict(bullying_text)
    legal_out = mapper.map_law(bullying_text, pred["toxic_score"], pred["threat_score"])
    severity = legal_out["severity"]
    legal_str = ",".join(legal_out.get("legal_sections", []))

    insert_complaint(
        victim_name=victim_name,
        platform=platform,
        bullying_text=bullying_text,
        screenshot_path=screenshot_path,
        toxic_score=pred["toxic_score"],
        threat_score=pred["threat_score"],
        severity=severity,
        legal_section=legal_str,
        status="Pending"
    )

    return jsonify({
        "message": "Complaint submitted",
        "severity": severity,
        "legal_section": legal_str
    })

@app.get("/api/dashboard")
def api_dashboard():
    counts = fetch_counts()
    recent = fetch_recent(limit=10)

    complaints = []
    for (cid, vname, platform, severity, status, created_at) in recent:
        complaints.append({
            "id": cid,
            "name": vname,
            "platform": platform,
            "severity": severity,
            "status": status,
            "created_at": created_at
        })

    return jsonify({
        **counts,
        "complaints": complaints
    })


if __name__ == "__main__":
    app.run(debug=True)

#, use_reloader=False