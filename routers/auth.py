from fastapi import Request, Response, status
from fastapi import APIRouter
from services.db import conn

router = APIRouter()

@router.post("/sign-up")
async def function(request: Request, response: Response):
    body = await request.json()
    email = body.get("email")
    password = body.get("password")
    device = body.get("device")
    ip = body.get("ip")

    # 1- check if we have email and password from the body
    if not email and not password:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "message": "Email and password are required",
            "metadata": {}
        }

    # 2- check if user already exisit
    cur = conn.cursor()
    user = conn.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,)).fetchone()
    if user:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "success": False,
            "message": "User already exists",
            "metadata": {}
        }

    # 3- save user data in database with "Pending" status

    # 4- send OTP to email


    return {
        "success": True,
        "message": "Account Created Successfully",
        "metadata": {}
    }