from datetime import datetime
import psycopg2
from fastapi import APIRouter, Request
from services.db import conn
import psycopg2.extras
import json
from worker.tasks import process_event

router = APIRouter()

@router.post("/{source}")
async def webhook(source: str, request: Request):

    data = await request.json()

    # SAVE RECEIVED TO THE "events" IN  DATABASE
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        INSERT INTO events (date, status, metadata, workflow_id)
        VALUES (%s, %s, %s, %s)
        RETURNING *
    """, (datetime.now(), "Pending", json.dumps(data), str(source).split("#")[0]))

    event_id = cur.fetchone()[0]
    conn.commit()

    # GET THE WORKFLOW FROM THE DATABASE
    cur.execute("SELECT * FROM workflows WHERE id = %s LIMIT 1", (str(source).split("#")[0],))
    workflow = cur.fetchone()

    print(dict(workflow))

    cur.execute("SELECT * FROM integrations WHERE user_id = %s", (dict(workflow).get("user_id"),))
    integrations = cur.fetchall()

    print([dict(integration) for integration in integrations])

    process_event.delay(event_id, data, dict(workflow), [dict(integration) for integration in integrations])

    return {"status": "success", "data": data, "event_id": event_id}