from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import RedirectResponse
import psycopg2.extras
from services.db import conn
import os, httpx, base64, json
from dotenv import load_dotenv
import uuid

load_dotenv()

router = APIRouter()


def userID(id: str): 
    return {
        "user_id": id,
    }
    

# NOTION ------------------------------------------------------

CLIENT_ID = os.getenv("NOTION_CLIENT_ID")
CLIENT_SECRET = os.getenv("NOTION_CLIENT_SECRET")
REDIRECT = os.getenv("NOTION_REDIRECT_URI")
AUTH_URL = os.getenv("NOTION_AUTH_URL")

@router.get("/notion")
def notion_login():
    return RedirectResponse(AUTH_URL)

@router.get("/notion/callback")
async def notion_callback(request: Request):
    code = request.query_params.get("code")

    basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.notion.com/v1/oauth/token",
            headers={
                "Authorization": f"Basic {basic}",
                "Content-Type": "application/json"
            },
            json={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT
            }
        )

    data = r.json()

    integrationID = str(uuid.uuid4())

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO integrations 
        (id, user_id, app_id, metadata)
        VALUES (%s,%s,%s,%s)
    """, (
        integrationID,
        "4c578f4a-1bd5-4735-9f16-03b5d4245969",
        1,
        json.dumps(data)
    ))
    conn.commit()

    return {
        "status": "connected",
        "message": "OAuth connected successfully (Notion)",
        "metadata": {
            "workspace_id": data["workspace_id"],
            "workspace_name": data["workspace_name"],
            "bot_id": data["bot_id"],
            "access_token": data["access_token"]
        }
    }