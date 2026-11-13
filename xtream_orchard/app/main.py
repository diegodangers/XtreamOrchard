"""XtreamOrchard development API with authenticated management endpoints."""
from pathlib import Path
import os
import secrets
import sqlite3

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .xtream import XtreamClient, XtreamCredentials, XtreamError, normalize_channels
from .console import register_console

DB = Path(os.getenv("XTREAM_ORCHARD_DB", "/data/xtream_orchard.db"))
app = FastAPI(title="XtreamOrchard", version="0.2.0")
register_console(app)


def require_admin(authorization: str | None = Header(default=None)):
    expected = os.getenv("XTREAM_ORCHARD_ADMIN_TOKEN", "")
    if not expected or not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Unauthorized")
    if not secrets.compare_digest(authorization[7:], expected):
        raise HTTPException(401, "Unauthorized")


def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS channels (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT '',
            visible INTEGER NOT NULL DEFAULT 0,
            position INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS revisions (
            id INTEGER PRIMARY KEY CHECK (id=1),
            version INTEGER NOT NULL
        );
        INSERT OR IGNORE INTO revisions VALUES (1, 0);
    """)
    return db


class Channel(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: str = ""


class Visibility(BaseModel):
    visible: bool


class BulkVisibility(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=5000)
    visible: bool


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/channels", dependencies=[Depends(require_admin)])
def channels():
    with connect() as db:
        return [dict(row) for row in db.execute(
            "SELECT * FROM channels ORDER BY position, name"
        )]


def store_channels(items: list[Channel]):
    with connect() as db:
        for index, item in enumerate(items):
            db.execute(
                """INSERT INTO channels(id,name,category,position)
                   VALUES(?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET
                   name=excluded.name,category=excluded.category""",
                (item.id, item.name, item.category, index),
            )
        db.execute("UPDATE revisions SET version=version+1 WHERE id=1")
    return {"imported": len(items)}


@app.post("/api/v1/channels/import", dependencies=[Depends(require_admin)])
def import_channels(items: list[Channel]):
    return store_channels(items)


@app.post("/api/v1/providers/xtream/refresh", dependencies=[Depends(require_admin)])
async def refresh_xtream():
    base = os.getenv("XTREAM_ORCHARD_PROVIDER_URL")
    username = os.getenv("XTREAM_ORCHARD_PROVIDER_USERNAME")
    password = os.getenv("XTREAM_ORCHARD_PROVIDER_PASSWORD")
    if not all((base, username, password)):
        raise HTTPException(503, "Provider not configured")
    try:
        credentials = XtreamCredentials(base, username, password)
        async with httpx.AsyncClient(trust_env=False) as client:
            provider = XtreamClient(credentials, client)
            await provider.authenticate()
            categories = await provider.categories()
            streams = await provider.live_streams()
        items = [Channel(**row) for row in normalize_channels(streams, categories)]
    except XtreamError as exc:
        # Only sanitized, credential-free diagnostics from XtreamClient reach the UI.
        raise HTTPException(502, str(exc)) from None
    except ValueError:
        raise HTTPException(400, "Invalid provider URL or credentials configuration") from None
    return store_channels(items)


@app.patch("/api/v1/channels/{channel_id}/visibility", dependencies=[Depends(require_admin)])
def set_visibility(channel_id: str, payload: Visibility):
    with connect() as db:
        cursor = db.execute(
            "UPDATE channels SET visible=? WHERE id=?",
            (int(payload.visible), channel_id),
        )
        if not cursor.rowcount:
            raise HTTPException(404, "Channel not found")
        db.execute("UPDATE revisions SET version=version+1 WHERE id=1")
    return {"id": channel_id, "visible": payload.visible}


@app.post("/api/v1/channels/visibility", dependencies=[Depends(require_admin)])
def set_bulk_visibility(payload: BulkVisibility):
    """Apply one atomic visibility update; unknown IDs reject the entire batch."""
    ids = list(dict.fromkeys(payload.ids))
    with connect() as db:
        placeholders = ",".join("?" for _ in ids)
        existing = db.execute(
            f"SELECT id FROM channels WHERE id IN ({placeholders})", ids
        ).fetchall()
        if len(existing) != len(ids):
            raise HTTPException(404, "One or more channels not found")
        db.execute(
            f"UPDATE channels SET visible=? WHERE id IN ({placeholders})",
            [int(payload.visible), *ids],
        )
        db.execute("UPDATE revisions SET version=version+1 WHERE id=1")
    return {"updated": len(ids), "visible": payload.visible}


@app.get("/api/v1/config", dependencies=[Depends(require_admin)])
def config():
    with connect() as db:
        version = db.execute(
            "SELECT version FROM revisions WHERE id=1"
        ).fetchone()[0]
        visible = [dict(row) for row in db.execute(
            """SELECT id,name,category,position FROM channels
               WHERE visible=1 ORDER BY position,name"""
        )]
    return {"version": version, "channels": visible}
