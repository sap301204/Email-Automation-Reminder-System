# Email Automation & Reminder System

Industry-oriented Email Automation & Reminder System built with **Python (FastAPI)** and a small **Next.js** dashboard. Supports scheduled and recurring reminders (RRULE), template rendering (Jinja2 + Markdown), async sending via SMTP (aiosmtplib), and basic tracking (open pixel + click redirect). SQLite used by default; can be swapped for Postgres.

## Features
- Create Contacts, Templates, Campaigns, and Reminders via API or UI
- RRULE recurrence support (RFC5545)
- Jinja2 templating + Markdown -> HTML rendering
- Async SMTP sending with retries & basic idempotency
- Open pixel and click redirect endpoints for tracking
- Minimal Next.js client demo for quick testing

## Tech Stack
- Python 3.11+, FastAPI, SQLAlchemy
- aiosmtplib (SMTP sending)
- Jinja2, markdown, python-dateutil
- SQLite (default), Postgres supported

## Quickstart (local)
1. Clone:
   ```bash
   git clone <repo-url>
   cd email-automation
   ```

2. Setup:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Create DB:
   ```bash
   mkdir -p db
   sqlite3 db/email.db < db/schema.sql
   ```

4. Set SMTP env vars (example for Gmail app password):
   ```bash
   export SMTP_HOST=smtp.gmail.com
   export SMTP_PORT=465
   export SMTP_USER=youremail@gmail.com
   export SMTP_PASS=<app-password>
   ```

5. Start API:
   ```bash
   uvicorn api.app:app --reload --port 8000
   ```

6. Start worker:
   ```bash
   python run_worker.py
   ```

7. Use Postman/curl or open the Next.js demo to create contacts/templates/campaigns/reminders. Example curl calls are in the docs.

## How it works (summary)
- Create a Reminder (one-off or with RRULE) via API.
- Worker loop runs every 15s:
  - `plan_next_fires`: expands RRULEs to create `messages` rows when due.
  - `dispatch_due`: selects scheduled messages whose `scheduled_at_utc <= now` and sends them.
- After sending, `messages` row updated to `sent` or `failed`.
- Open pixel `/t/o/{message_id}.png` and click redirect `/t/c/{message_id}` update status.

## Safety & Production Notes
- Respect unsubscribe flags (`contacts.unsubscribed`).
- Add rate-limiting when sending at scale.
- Use Postgres and a proper queue (Redis + RQ/Celery) for scale.
- Use DKIM/SPF and provider APIs for better deliverability.
- Add observability (metrics, logs, Sentry).

## License
MIT — see LICENSE file.
