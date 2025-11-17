from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize database (used in cura_app.py)
db = SQLAlchemy()

# ---------- USER MODEL ----------
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))          # ✅ New field for phone number
    dob = db.Column(db.String(20))            # ✅ New field for Date of Birth (string for easy HTML form)
    gender = db.Column(db.String(10))         # ✅ New field for gender
    role = db.Column(db.String(50), default='user', nullable=False)

    feedbacks = db.relationship(
        'Feedback', backref='user', lazy=True, cascade="all, delete"
    )

    def __repr__(self):
        return f"<User {self.email}>"

# ---------- FEEDBACK MODEL ----------
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False
    )
    message = db.Column(db.Text, nullable=False)
    reviewed = db.Column(db.Boolean, default=False, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Feedback {self.id} (User {self.user_id})>"

# ---------- USER ACTIVITY LOG (for charts/dashboard) ----------
class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    date = db.Column(db.String(20))  # Example: "Fri", "Sat"
    symptoms_analyzed = db.Column(db.Integer, default=0)
    diet_visits = db.Column(db.Integer, default=0)
    mental_visits = db.Column(db.Integer, default=0)  # ✅ NEW FIELD

    # REMOVE mood_score, steps_walked if unused
