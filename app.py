import os, uuid, datetime as dt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, text
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "email.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, future=True, connect_args={"check_same_thread": False})

# ensure schema exists
schema_file = Path(__file__).resolve().parent.parent / "db" / "schema.sql"
with engine.begin() as conn:
    if schema_file.exists():
        conn.execute(text(schema_file.read_text()))
    else:
        raise RuntimeError("schema.sql missing in db/")

app = FastAPI(title="Email Automation API")

class Contact(BaseModel):
    name: str
    email: EmailStr
    timezone: str = "Asia/Kolkata"

class Template(BaseModel):
    name: str
    subject: str
    body_md: str

class Campaign(BaseModel):
    name: str
    template_id: str
    sender_name: str
    sender_email: EmailStr

class Reminder(BaseModel):
    title: str
    contact_id: str
    campaign_id: str
    start_at_utc: str
    rrule: str | None = None

@app.post("/contacts")
def create_contact(c: Contact):
    with engine.begin() as db:
        cid = str(uuid.uuid4())
        db.execute(text("INSERT INTO contacts(id,name,email,timezone) VALUES(:i,:n,:e,:tz)"),
                   dict(i=cid,n=c.name,e=c.email,tz=c.timezone))
        return {"id": cid}

@app.post("/templates")
def create_template(t: Template):
    with engine.begin() as db:
        tid = str(uuid.uuid4())
        db.execute(text("INSERT INTO templates(id,name,subject,body_md,created_at) VALUES(:i,:n,:s,:b,:ts)"),
                   dict(i=tid,n=t.name,s=t.subject,b=t.body_md,ts=dt.datetime.utcnow().isoformat()))
        return {"id": tid}

@app.post("/campaigns")
def create_campaign(c: Campaign):
    with engine.begin() as db:
        # ensure template exists
        row = db.execute(text("SELECT id FROM templates WHERE id=:id"), dict(id=c.template_id)).fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="template_id not found")
        cid = str(uuid.uuid4())
        db.execute(text("""INSERT INTO campaigns(id,name,template_id,sender_name,sender_email,created_at)
                           VALUES(:i,:n,:t,:sn,:se,:ts)"""),
                   dict(i=cid,n=c.name,t=c.template_id,sn=c.sender_name,se=c.sender_email,ts=dt.datetime.utcnow().isoformat()))
        return {"id": cid}

@app.post("/reminders")
def create_reminder(r: Reminder):
    with engine.begin() as db:
        # validate contact and campaign
        if not db.execute(text("SELECT id FROM contacts WHERE id=:id"), dict(id=r.contact_id)).fetchone():
            raise HTTPException(status_code=400, detail="contact_id not found")
        if not db.execute(text("SELECT id FROM campaigns WHERE id=:id"), dict(id=r.campaign_id)).fetchone():
            raise HTTPException(status_code=400, detail="campaign_id not found")
        rid = str(uuid.uuid4())
        db.execute(text("""INSERT INTO reminders(id,title,contact_id,campaign_id,start_at_utc,rrule,active)
                           VALUES(:i,:t,:ct,:ca,:st,:rr,1)"""),
                   dict(i=rid,t=r.title,ct=r.contact_id,ca=r.campaign_id,st=r.start_at_utc,rr=r.rrule))
        return {"id": rid}

@app.get("/messages/due")
def list_due(limit: int = 50):
    with engine.begin() as db:
        rows = db.execute(text("SELECT * FROM messages WHERE status='scheduled' ORDER BY scheduled_at_utc LIMIT :l"), dict(l=limit)).fetchall()
        return [dict(row._mapping) for row in rows]

@app.get("/health")
def health():
    return {"ok": True}
