from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
from models import db, User, Feedback,UserLog
from datetime import datetime

# ---------- APP CONFIG ----------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cura-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'database', 'cura.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs("database", exist_ok=True)
db.init_app(app)

# ---------- LOGIN MANAGER ----------
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- GUEST LOGIN ----------
@app.route("/guest")
def guest_login():
    logout_user() 
    session["role"] = "guest"
    flash("You're exploring Cura as a Guest. Register to unlock full features!", "info")
    return redirect(url_for("index"))

# ---------- PROFILE FEATURE ----------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.name = request.form.get("name")
        current_user.phone = request.form.get("phone")
        current_user.dob = request.form.get("dob")
        current_user.gender = request.form.get("gender")

        new_password = request.form.get("password")
        if new_password:
            current_user.password = generate_password_hash(new_password)

        db.session.commit()
        flash("✅ Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=current_user)

# ---------- STATIC ROUTES ----------
@app.route("/")
def index():
    return render_template("base.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

# ---------- CONTACT US ----------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name") or "Anonymous"
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        # Create Feedback entry (guest or user)
        user_id = current_user.id if current_user.is_authenticated else None

        feedback = Feedback(
            user_id=user_id if user_id else 0,  # 0 means guest
            message=f"📩 Contact Form Submission\n"
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Phone: {phone}\n\n"
                    f"Message: {message}"
        )

        db.session.add(feedback)
        db.session.commit()

        flash("✅ Your message has been sent! Our team will contact you soon.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# ---------- DIET AND NUTRITION ----------
@app.route("/diet_nutrition")
@login_required
def diet_nutrition():
    from datetime import datetime

    log = UserLog(
        user_id=current_user.id,
        date=datetime.utcnow().strftime("%a"),
        diet_visits=1
    )
    db.session.add(log)
    db.session.commit()

    return render_template("diet_nutrition.html")

# ---------- SYMPTOM ANALYZER ----------
@app.route("/analyze", methods=["GET", "POST"])
@login_required
def analyze():
    import google.generativeai as genai
    analysis = None

    if request.method == "POST":
        symptoms = request.form["symptoms"].strip()
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = (
                f"User symptoms: {symptoms}\n\n"
                "You are Cura, a helpful AI assistant. Provide a short summary of possible causes "
                "and 3 lifestyle tips under 150 words."
            )
            response = model.generate_content(prompt)
            analysis = getattr(response, "text", "⚠️ Unable to read response.")

            # ✅ Log user activity (Symptom Analyzer usage)
            if current_user.is_authenticated:
                log_entry = UserLog(
                    user_id=current_user.id,
                    date=datetime.utcnow().strftime("%a"),
                    symptoms_analyzed=1  # count one usage
                )
                db.session.add(log_entry)
                db.session.commit()

        except Exception as e:
            analysis = f"⚠️ Error during analysis: {e}"

    return render_template("analyze.html", analysis=analysis)

# ---------- MENTAL HEALTH HUB ----------
@app.route("/mental", methods=["GET", "POST"])
@login_required
def mental_health():
    import google.generativeai as genai
    from datetime import datetime

    alert = None
    ai_response = None

    # --- Log MENTAL VISIT ---
    today = datetime.utcnow().strftime("%a")
    log = UserLog.query.filter_by(user_id=current_user.id, date=today).first()

    if not log:
        log = UserLog(
            user_id=current_user.id,
            date=today,
            mental_visits=1
        )
        db.session.add(log)
    else:
        log.mental_visits += 1

    db.session.commit()
    # ------------------------

    # If user submitted a message
    if request.method == "POST":
        feeling = request.form["feeling"].lower()

        # Crisis detection
        crisis_keywords = ["suicide", "kill myself", "end my life", "die"]
        if any(word in feeling for word in crisis_keywords):
            alert = (
                "🚨 If you are in danger, please contact a trusted person or "
                "local helpline immediately."
            )

        # Generate supportive AI reply
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

            prompt = (
                f"The user says: '{feeling}'. Provide a supportive, gentle, 2–3 line "
                "message. Do not diagnose. Be comforting."
            )

            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)

            ai_response = response.text.strip()

        except Exception:
            ai_response = "⚠️ Could not process your message."

    return render_template("mental_health.html", alert=alert, ai_response=ai_response)

# ---------- CHATBOT ----------
@app.route("/predict", methods=["POST"])
def predict():
    import random
    from flask import session, jsonify
    from flask_login import current_user

    data = request.get_json()
    user_msg = data.get("message", "").lower()
    role = session.get("role") or ("guest" if not current_user.is_authenticated else current_user.role)

    # -----------------------------------------------------------
    # 🆘 FIRST AID EMERGENCY SYSTEM (Works even in guest mode)
    # -----------------------------------------------------------
    first_aid_tips = {
        "burn": "🔥 <b>First Aid for Burns</b><br>• Cool burn under running water 20 minutes<br>• Do NOT use ice or toothpaste<br>• Cover with clean cloth<br>• Seek help if blistering or deep burn",
        "bleeding": "🩸 <b>First Aid for Bleeding</b><br>• Apply firm pressure with cloth<br>• Keep injured part elevated<br>• Do NOT remove soaked cloth—add more<br>• Seek medical help if not stopping",
        "choking": "🫁 <b>First Aid for Choking</b><br>• Encourage coughing<br>• If unable to breathe: 5 back blows + 5 thrusts<br>• Call emergency services",
        "fracture": "🦴 <b>First Aid for Fracture</b><br>• Keep injured area still<br>• Do NOT straighten bone<br>• Apply cold pack<br>• Seek medical attention",
        "faint": "😵 <b>First Aid for Fainting</b><br>• Lay person flat & elevate legs<br>• Loosen clothing<br>• Allow airflow<br>• If unconscious > 1 min, seek help",
        "snake": "🐍 <b>First Aid for Snake Bite</b><br>• Keep person calm<br>• Immobilize limb<br>• Do NOT suck venom or apply ice<br>• Go to hospital immediately",
        "asthma": "💨 <b>First Aid for Asthma Attack</b><br>• Sit upright<br>• Use inhaler: 1 puff every 30–60 sec (max 10)<br>• Seek help if no improvement",
        "heart attack": "❤️ <b>Heart Attack First Aid</b><br>• Call emergency services<br>• Keep person calm & seated<br>• Loosen tight clothes<br>• If unresponsive: start CPR if trained"
    }

    for keyword, tip in first_aid_tips.items():
        if keyword in user_msg:
            return jsonify({"answer": tip})

    # -----------------------------------------------------------
    # 🚫 Restrict guest access to protected tools
    # -----------------------------------------------------------
    restricted_keywords = ["diet", "nutrition", "mental", "health hub", "symptom", "analyze", "checker"]
    if role == "guest" and any(k in user_msg for k in restricted_keywords):
        response = (
            "⚠️ You're currently exploring Cura as a <b>Guest</b>.<br><br>"
            "These tools are available only for registered users:<br>"
            "• Symptom Analyzer<br>"
            "• Mental Health Hub<br>"
            "• Diet & Nutrition<br><br>"
            "👉 Please <a href='/register' style='color:#E0AAFF;'>register here</a> to unlock full access. 💫"
        )
        return jsonify({"answer": response})

    # -----------------------------------------------------------
    # 🤖 CURA Knowledge & Features
    # -----------------------------------------------------------
    if any(w in user_msg for w in ["who created", "developer", "made cura"]):
        response = (
            "👩‍💻 CURA was developed by a team of students and developers-"
            " Aadhav Gugan, GYR Saran, Sai Prasad Reddy, SV Manoj Kumar"
            "to make AI-powered healthcare accessible to everyone."
        )

    elif any(w in user_msg for w in ["what is cura", "about cura", "tell me about cura"]):
        response = (
            "🤖 <b>CURA</b> = Care, Understand, Respond, Assist.<br>"
            "Your personal AI Health & Wellness Assistant."
        )

    elif any(w in user_msg for w in ["patient tools", "features", "help", "what can you do"]):
        response = (
            "🩺 You can explore these patient tools:<br>"
            "• <b>Symptom Checker</b><br>"
            "• <b>Mental Health Hub</b><br>"
            "• <b>Diet & Nutrition</b><br>"
            "Would you like me to open one for you?"
        )

    elif any(w in user_msg for w in ["diet", "nutrition"]):
        response = (
            "🥗 Explore our <b>Diet & Nutrition</b> section for meal plans.<br>"
            "👉 <a href='/diet_nutrition'>Open Diet Plans</a>"
        )

    elif any(w in user_msg for w in ["symptom", "doctor", "analyze"]):
        response = (
            "🧠 Use our <b>Symptom Analyzer</b> for quick insights.<br>"
            "👉 <a href='/analyze'>Try Symptom Checker</a>"
        )

    elif any(w in user_msg for w in ["mental", "stress", "mood"]):
        response = (
            "🧘 Visit the <b>Mental Health Hub</b> for support.<br>"
            "👉 <a href='/mental'>Open Mental Health Hub</a>"
        )

    elif any(w in user_msg for w in ["wellness tip", "health tip", "motivate", "daily tip"]):
        tips = [
            "💧 Stay hydrated!",
            "🌙 Sleep 7 hours for better recovery.",
            "🚶 Walk 20 minutes daily.",
            "🥦 Eat something green today!",
            "🧘 Deep breathing lowers stress immediately."
        ]
        response = random.choice(tips)

    elif any(w in user_msg for w in ["contact", "help center", "support"]):
        response = (
            "📩 Contact support anytime:<br>"
            "<a href='mailto:support@cura.ai'>support@cura.ai</a>"
        )

    elif "register" in user_msg or "sign up" in user_msg:
        response = (
            "✨ You can <a href='/register' style='color:#E0AAFF;'>register here</a> "
            "to unlock all of CURA’s features!"
        )

    # -----------------------------------------------------------
    # DEFAULT FALLBACK RESPONSE
    # -----------------------------------------------------------
    else:
        response = (
            "🤖 I’m <b>Cura</b> — your AI health assistant! Ask me:<br>"
            "• First Aid Tips<br>"
            "• Show me diet plans<br>"
            "• Give me a wellness tip<br>"
            "• How to manage stress"
        )

    return jsonify({"answer": response})

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():

    # If user is logged in (NOT guest), block registration
    if current_user.is_authenticated and session.get("role") != "guest":
        flash("You already have an account. Please log in instead.", "warning")
        return redirect(url_for("login"))

    # If in guest mode → allow registration (remove guest mode)
    if session.get("role") == "guest":
        session.pop("role", None)  # remove guest

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Email already exists — redirect to login
        if User.query.filter_by(email=email).first():
            flash("This email already exists. Please log in.", "danger")
            return redirect(url_for("login"))

        hashed_pw = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # ✅ Clear guest status
            session.pop("role", None)
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("login.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    session.clear()  # ✅ Always clears guest flags
    flash("You have been logged out.", "info")
    session.pop("admin_verified", None)
    return redirect(url_for("index"))

# ---------- FEEDBACK DASHBOARD ----------
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        feedback_msg = request.form["message"]
        new_feedback = Feedback(user_id=current_user.id, message=feedback_msg)
        db.session.add(new_feedback)
        db.session.commit()
        flash("Feedback submitted successfully!", "success")
        return redirect(url_for("dashboard"))

    feedbacks = Feedback.query.filter_by(user_id=current_user.id).order_by(Feedback.date_submitted.desc()).all()
    return render_template("dashboard.html", name=current_user.name, feedbacks=feedbacks)

# ---------- REVIEWER DASHBOARD ----------
@app.route("/reviewer", methods=["GET", "POST"])
@login_required
def reviewer_dashboard():
    if getattr(current_user, "role", "user") != "reviewer":
        flash("Access denied. Reviewer only.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        fid = request.form.get("feedback_id")
        fb = Feedback.query.get(fid)
        if fb:
            fb.reviewed = True
            db.session.commit()
            flash(f"Feedback #{fid} marked as reviewed.", "success")
        return redirect(url_for("reviewer_dashboard"))

    feedbacks = Feedback.query.order_by(Feedback.date_submitted.desc()).all()
    return render_template("reviewer_dashboard.html", feedbacks=feedbacks)

# ---------- ADMIN PANEL ----------
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_panel():

    # STEP 1: If already verified admin / reviewer → show table
    if session.get("admin_verified") or current_user.role in ["reviewer", "admin"]:
        users = User.query.order_by(User.id.asc()).all()
        return render_template("admin_panel.html", users=users)

    # STEP 2: Not verified yet → Show password screen
    if request.method == "POST":
        password = request.form.get("admin_password")

        if password == "curaadmin123":
            # Upgrade user to reviewer (one-time upgrade)
            current_user.role = "reviewer"
            db.session.commit()

            # Remember admin session until logout
            session["admin_verified"] = True

            flash("✅ Admin access verified successfully!", "success")
            return redirect(url_for("admin_panel"))
        else:
            flash("❌ Incorrect Admin password.", "danger")

    # Show the admin password form
    return render_template("admin_panel.html", users=None)

# ---------- USER HEALTH DASHBOARD ----------
@app.route("/user_dashboard")
@login_required
def user_dashboard():
    logs = UserLog.query.filter_by(user_id=current_user.id).order_by(UserLog.id.asc()).all()

    grouped = {}  
    # example structure:
    # { 
    #   "Fri": {"diet": 2, "symptoms": 1, "mental": 3}
    # }

    for log in logs:
        day = log.date

        if day not in grouped:
            grouped[day] = {
                "diet": 0,
                "symptoms": 0,
                "mental": 0
            }

        grouped[day]["diet"] += log.diet_visits
        grouped[day]["symptoms"] += log.symptoms_analyzed
        grouped[day]["mental"] += log.mental_visits 

    dates = list(grouped.keys())
    diet_visits = [grouped[d]["diet"] for d in dates]
    symptom_uses = [grouped[d]["symptoms"] for d in dates]
    mental_visits = [grouped[d]["mental"] for d in dates] 

    return render_template(
        "user_dashboard.html",
        dates=dates,
        diet_visits=diet_visits,
        symptom_uses=symptom_uses,
        mental_visits=mental_visits 
    )

# ---------- MAIN ----------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
