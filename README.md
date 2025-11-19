🌟 CURA — AI Health Assistant:

CURA (Care • Understand • Respond • Assist) is an AI-powered personal health assistant built using Flask, HTML/CSS/JS, and Machine Learning.
It helps users analyze symptoms, get mental wellness support, track health usage, and receive nutritional guidance.

🚀 Features:
🧠 AI Chatbot (CURA Bot)

Smart responses

First-aid emergency tips

Wellness tips

Symptom & diet guidance

Works even in Guest Mode

🩺 Symptom Analyzer

Users describe symptoms

AI provides safe, simple health insights

Logged to user dashboard

🧘 Mental Health Hub

Supportive AI messages

Crisis keyword detection

Tracks usage in dashboard

🍎 Diet & Nutrition Plans

6 structured diet plans

Click to reveal full plan

Healthy lifestyle suggestions

📊 User Health Dashboard

Track daily usage:

Diet page visits

Symptom analyzer usage

Mental health hub visits

Automatic graph visualization using Chart.js

🔐 Authentication System

Register / Login

Guest Mode (limited access)

Email uniqueness check

Flash messages for success/errors

🛠️ Admin Panel

Protect with admin password

View all registered users

Reviewer/admin role support

📁 Project Structure:
/project-root
│
├── app.py
├── models.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── user_dashboard.html
│   ├── admin_panel.html
│   ├── diet.html
│   ├── mental_health.html
│   └── analyze.html
│
├── static/
│   ├── style.css
│   ├── images/
│   └── js/
│
└── database.sqlite3

🎯 Guest Mode:
Guests can chat with Cura and get first-aid tips, but they cannot access:

❌ Symptom Analyzer
❌ Diet & Nutrition
❌ Mental Health Hub
❌ User Dashboard

They will be redirected to register.

🔥 Technologies Used:
Flask

SQLite

Chart.js

HTML5 / CSS3 / JS

Gemini API (AI responses)

Flask-Login

Bootstrap / Custom UI

This project is developed as a complete AI-health assistant system to support learning, healthcare exploration, and personal wellness tracking.
│
└── database.sqlite3
