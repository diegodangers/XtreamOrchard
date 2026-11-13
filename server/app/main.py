"""XtreamOrchard development API; no live provider integration or authentication."""
from pathlib import Path
import os
import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB = Path(os.getenv("XTREAM_ORCHARD_DB", "/data/xtream_orchard.db"))
app = FastAPI(title="XtreamOrchard", version="0.1.0")


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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/channels")
def channels():
    with connect() as db:
        return [dict(row) for row in db.execute(
            "SELECT * FROM channels ORDER BY position, name"
        )]


@app.post("/api/v1/channels/import")
def import_channels(items: list[Channel]):
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


@app.patch("/api/v1/channels/{channel_id}/visibility")
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


@app.get("/api/v1/config")
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
