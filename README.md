Email Automation & Reminder System

A fully modular, production-oriented Email Automation & Reminder System built with Python (FastAPI + SQLAlchemy) and a Next.js dashboard.
The system schedules one-time or recurring reminders, renders dynamic templates, sends emails asynchronously via SMTP, and tracks opens/clicks via webhooks.

🚀 Features

✔ Create Contacts, Templates, Campaigns, Reminders

✔ Schedule recurring reminders using RRULE

✔ Jinja2 + Markdown → HTML templating

✔ Async SMTP sender (aiosmtplib)

✔ Worker loop for automated dispatch

✔ Email tracking (open pixel + click redirect)

✔ SQLite by default (Postgres-ready)

✔ Minimal Next.js dashboard for easy testing

🧱 Tech Stack
Layer	Technology
API	FastAPI
DB	SQLite (with SQLAlchemy)
Rendering	Jinja2 + Markdown
Scheduling	APScheduler-style async loop
Email Sender	aiosmtplib
Dashboard	Next.js (App Router)
Worker	Python async cron-loop
📁 Project Structure

email-automation/
├─ api/
├─ src/
│  ├─ renderer.py
│  ├─ mailer.py
│  ├─ scheduler.py
│  ├─ webhooks.py
├─ db/
├─ apps/web/
├─ run_worker.py
├─ requirements.txt
├─ README.md
├─ LICENSE
└─ .gitignore

🛠 Setup Instructions
1. Install dependencies
pip install -r requirements.txt
2. Initialize the database
sqlite3 db/email.db < db/schema.sql
3. Set SMTP environment variables
(Example for Gmail App Password)
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=465
export SMTP_USER=youremail@gmail.com
export SMTP_PASS=your-app-password
4. Run the FastAPI backend
uvicorn api.app:app --reload --port 8000
5. Start the Worker Scheduler
python run_worker.py
6. Launch the Dashboard (Next.js)
cd apps/web
npm install
npm run dev

📦 API Endpoints

POST /contacts
POST /templates
POST /campaigns
POST /reminders
GET /messages/due
GET /health
Tracking:
/t/o/{message_id}.png → open
/t/c/{message_id}?url=... → click

🛡 Production Notes

Add SPF + DKIM for better deliverability
Move to Postgres for scaling
Add Redis queue for large-volume sends
Add rate-limits & unsubscribe handling

📄 License

This project is licensed under the MIT License — free to use, modify, and distribute.
