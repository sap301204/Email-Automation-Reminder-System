import base64
from fastapi import APIRouter, Response, Request
from sqlalchemy import create_engine, text
from pathlib import Path

router = APIRouter()
DB_PATH = Path(__file__).resolve().parent.parent / "db" / "email.db"
engine = create_engine(f"sqlite:///{DB_PATH}", future=True, connect_args={"check_same_thread": False})

_pixel = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGP4BwQACfsD/UE8oRUAAAAASUVORK5CYII=")

@router.get("/t/o/{message_id}.png")
def opened(message_id: str):
    with engine.begin() as db:
        db.execute(text("UPDATE messages SET status='opened' WHERE id=:id AND status='sent'"), dict(id=message_id))
    return Response(content=_pixel, media_type="image/png")

@router.get("/t/c/{message_id}")
def clicked(message_id: str, url: str):
    with engine.begin() as db:
        db.execute(text("UPDATE messages SET status='clicked' WHERE id=:id AND status IN ('sent','opened')"), dict(id=message_id))
    return Response(status_code=302, headers={"Location": url})
