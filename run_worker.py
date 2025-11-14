import os, asyncio, datetime as dt
from sqlalchemy import create_engine
from src.mailer import Mailer
from src import scheduler as sched_module
from src import renderer as renderer_module
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "db" / "email.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, future=True, connect_args={"check_same_thread": False})

async def main():
    mailer = Mailer(
        host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        port=int(os.getenv("SMTP_PORT", "465")),
        username=os.getenv("SMTP_USER"),
        password=os.getenv("SMTP_PASS"),
        use_tls=True
    )
    renderer = renderer_module
    print("Worker started. Press Ctrl+C to stop.")
    try:
        while True:
            now = dt.datetime.utcnow().replace(tzinfo=None)
            with engine.begin() as db:
                await sched_module.plan_next_fires(db, now)
                await sched_module.dispatch_due(db, mailer, now, renderer=renderer)
            await asyncio.sleep(15)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(main())
