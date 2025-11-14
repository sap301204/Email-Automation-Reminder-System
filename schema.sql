PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS contacts(
  id TEXT PRIMARY KEY,
  name TEXT,
  email TEXT UNIQUE,
  timezone TEXT DEFAULT 'Asia/Kolkata',
  unsubscribed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS templates(
  id TEXT PRIMARY KEY,
  name TEXT UNIQUE,
  subject TEXT,
  body_md TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS campaigns(
  id TEXT PRIMARY KEY,
  name TEXT,
  template_id TEXT,
  sender_name TEXT,
  sender_email TEXT,
  created_at TEXT,
  FOREIGN KEY(template_id) REFERENCES templates(id)
);

CREATE TABLE IF NOT EXISTS reminders(
  id TEXT PRIMARY KEY,
  title TEXT,
  contact_id TEXT,
  campaign_id TEXT,
  start_at_utc TEXT,
  rrule TEXT,
  active INTEGER DEFAULT 1,
  last_fired_at_utc TEXT,
  FOREIGN KEY(contact_id) REFERENCES contacts(id),
  FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
);

CREATE TABLE IF NOT EXISTS messages(
  id TEXT PRIMARY KEY,
  campaign_id TEXT,
  contact_id TEXT,
  scheduled_at_utc TEXT,
  sent_at_utc TEXT,
  provider_msg_id TEXT,
  status TEXT,
  subject TEXT,
  body_rendered_html TEXT,
  error TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_sched ON messages(scheduled_at_utc, status);
