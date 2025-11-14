import datetime as dt, uuid, pytz
from dateutil.rrule import rrulestr
from sqlalchemy import text

UTC = pytz.UTC

async def plan_next_fires(db, now_utc: dt.datetime):
    rows = db.execute(text("""SELECT id, contact_id, campaign_id, start_at_utc, rrule, last_fired_at_utc
                              FROM reminders WHERE active=1""")).fetchall()
    for r in rows:
        start = dt.datetime.fromisoformat(r.start_at_utc).replace(tzinfo=UTC)
        rule = r.rrule and rrulestr(r.rrule, dtstart=start)
        last = r.last_fired_at_utc and dt.datetime.fromisoformat(r.last_fired_at_utc).replace(tzinfo=UTC)
        next_fire = None
        if rule:
            next_fire = rule.after(last or (start - dt.timedelta(seconds=1)), inc=True)
        else:
            if (not last) and start <= now_utc:
                next_fire = start
        if next_fire and next_fire <= now_utc + dt.timedelta(minutes=1):
            mid = str(uuid.uuid4())
            db.execute(text("""INSERT INTO messages(id,campaign_id,contact_id,scheduled_at_utc,status)
                               VALUES (:id,:cid,:ct,:sch,'scheduled')"""),
                       dict(id=mid, cid=r.campaign_id, ct=r.contact_id, sch=next_fire.isoformat()))
            db.execute(text("UPDATE reminders SET last_fired_at_utc=:now WHERE id=:rid"),
                       dict(now=now_utc.isoformat(), rid=r.id))
    db.commit()

async def dispatch_due(db, mailer, now_utc: dt.datetime, renderer=None):
    due = db.execute(text("""SELECT m.id, m.campaign_id, m.contact_id, t.subject, t.body_md,
                                    c.name as cname, c.email as cemail, camp.sender_name, camp.sender_email
                             FROM messages m
                             JOIN campaigns camp ON camp.id=m.campaign_id
                             JOIN templates t ON t.id=camp.template_id
                             JOIN contacts c ON c.id=m.contact_id
                             WHERE m.status='scheduled' AND m.scheduled_at_utc <= :now"""),
                     dict(now=now_utc.isoformat())).fetchall()
    for row in due:
        subj, html = renderer.render_email(row.subject, row.body_md, {"name": row.cname})
        res = await mailer.send_html(row.sender_name, row.sender_email, row.cemail, subj, html)
        if res["ok"]:
            db.execute(text("""UPDATE messages SET status='sent', sent_at_utc=:now, body_rendered_html=:html, provider_msg_id=:pid, subject=:sub WHERE id=:id"""),
                       dict(now=now_utc.isoformat(), html=html, pid=res.get("provider_msg_id"), id=row.id, sub=subj))
        else:
            db.execute(text("UPDATE messages SET status='failed', error=:e WHERE id=:id"),
                       dict(e=res.get("error"), id=row.id))
    db.commit()
