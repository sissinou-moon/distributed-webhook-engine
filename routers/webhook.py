from datetime import datetime
import psycopg2
from fastapi import APIRouter, Request
from services.db import conn
import psycopg2.extras
import json
from services.worker.tasks import process_event

router = APIRouter()

@router.post("/{source}")
async def webhook(source: str, request: Request):

    data = await request.json()

    # SAVE RECEIVED TO THE "events" IN  DATABASE
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        INSERT INTO events (date, status, metadata)
        VALUES (%s, %s, %s)
        RETURNING *
    """, (datetime.now(), "Pending", json.dumps(data)))

    event_id = cur.fetchone()[0]
    conn.commit()

    process_event.delay(event_id, data)

    return {"status": "success", "data": data, "event_id": event_id}