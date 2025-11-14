'use client'
import { useState } from "react";

export default function Page(){
  const [status, setStatus] = useState("");
  async function createDemo(){
    setStatus("Creating demo...");
    // create contact
    const c = await fetch('/api/contacts',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({name:'Student A', email:'student@example.com'})}).then(r=>r.json());
    const t = await fetch('/api/templates',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({name:'Class Reminder', subject:'Reminder: {{name}} — session at 7 PM', body_md:'Hi {{name}},\n\nYour session begins at **7 PM**.'})}).then(r=>r.json());
    const camp = await fetch('/api/campaigns',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({name:'Tonight', template_id:t.id, sender_name:'Coach', sender_email:'coach@demo.com'})}).then(r=>r.json());
    const start = new Date(Date.now()+2*60*1000).toISOString();
    await fetch('/api/reminders',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({title:'Join Session', contact_id:c.id, campaign_id:camp.id, start_at_utc:start})});
    setStatus('Demo scheduled: email in ~2 minutes. Check inbox for student@example.com (or check messages table).');
  }
  return (<div style={{padding:20}}>
    <h1>Email Automation: Demo</h1>
    <button onClick={createDemo}>Create demo reminder (2 min)</button>
    <p>{status}</p>
  </div>);
}
