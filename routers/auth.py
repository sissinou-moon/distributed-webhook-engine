from datetime import datetime
import psycopg2
from fastapi import Request, Response, status
from fastapi import APIRouter
from services.db import conn
import psycopg2.extras
import uuid
from services.otp import sendOTP
import random
from services.password import hashPassword, verifyHasedPassword
from services.jwt import create_tokens, verify_access_token

router = APIRouter()

@router.post("/sign-up")
async def function(body: dict, response: Response):
    email = body.get("email")
    password = body.get("password")
    username = body.get("username")
    device = body.get("device")
    ip = body.get("ip")

    # 1- check if we have email and password from the body
    if not email or not password:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "message": "Email and password are required",
            "metadata": {}
        }

    # 2- check if user already exisit
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,))
    user = cur.fetchone()
    if user:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "success": False,
            "message": "User already exists",
        }

    # 3- save user data in database with "Pending" status 
    id = str(uuid.uuid4())
    hasedPassword = hashPassword(password)
    try:
        # comment: 
        cur.execute("INSERT INTO users (id, email, password, username, status, verified) VALUES (%s, %s, %s, %s, %s, %s)", (id, email, hasedPassword, username, "Active", False))
        conn.commit()
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "success": False,
            "message": "Internal Server Error",
            "metadata": {
                "error": str(e)
            }
        }

    # 4- send OTP to email
    otp = str(random.randint(100000, 999999))
    try:
        await sendOTP(email, otp)
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "success": False,
            "message": "Internal Server Error",
            "metadata": {
                "error": str(e)
            }
        }

    return {
        "success": True,
        "message": "Account Created And OTP Sent Successfully",
        "metadata": {
            "email": email,
            "username": username,
            "device": device,
            "ip": ip
        }
    }

@router.post("/send-otp")
async def function(body: dict, response: Response):

    # 1- GET EMAIL
    email = body.get("email")

    # 2- CHECK IF WE GOT THE EMAIL
    if not email:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "message": "Email is required to send OTP",
            "metadata": {}
        }

    # 3- CHECK IF ACCOUNT STATUS = ACTIVE
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT status FROM users WHERE email = %s", (email,))
    status = cur.fetchone()[0]

    if status != "Active":
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            "success": False,
            "message": "Account is not active",
            "metadata": {}
        }

    # 4- SEND OTP
    otp = str(random.randint(100000, 999999))
    try:
        await sendOTP(email, otp)
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "success": False,
            "message": "Internal Server Error",
            "metadata": {
                "error": str(e)
            }
        }

    return {
        "success": True,
        "message": "OTP sent successfully",
        "metadata": {}
    }

@router.get("/verify-otp")
async def function(body: dict, response: Response):

    # 1- GET EMAIL AND OTP
    email = body.get("email")
    otp = body.get("otp")

    # 2- CHECK IF WE GOT EMAIL AND OTP
    if not email or not otp:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "message": "Email and OTP are required",
            "metadata": {}
        }

    # 3- GET THE OTP FROM THE DATABASE & COMPARE IT WITH THE OTP WE GOT
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT otp FROM users WHERE email = %s", (email,))
    realOTP = cur.fetchone()[0]

    if realOTP != otp:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "success": False,
            "message": "Invalid OTP",
            "metadata": {}
        }

    # 4- CHANGE USER ACCOUNT TO VERIFIED
    cur.execute("""
UPDATE users
SET otp = NULL, verified = True
WHERE email = %s
    """, (email))
    conn.commit()

    return {
        "success": True,
        "message": "OTP verified successfully",
        # WE MUST RETURN ID, EMAIL, USERNAME 
        "metadata": {}
    }

@router.post("/access")
async def function(body: dict, response: Response):
    
    id = body.get("id")
    email = body.get("email")
    username = body.get("username")
    device = body.get("device")
    ip = body.get("ip")

    if not id or not email or not username:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "message": "All fields are required",
            "metadata": {}
        }

    # 3- REVOKE ALL OLD SESSIONS
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
UPDATE sessions
SET status = "REVOKED"
WHERE user_id = %s
    """, (id))
    conn.commit()

    # 4- CREATE NEW ACTIVE SESSION
    access_token, refresh_token = create_tokens(id)
    cur.execute("""
INSERT INTO sessions (id, user_id, status, refresh_token, device, ip, created_at,)
VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (str(uuid.uuid4()), id, "ACTIVE", refresh_token, device, ip, datetime.now()))
    conn.commit()
    
    return {
        "success": True,
        "message": "Tokens created successfully",
        "metadata": {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    }

@router.post("/verify-refresh_token")
async def function(body: dict, response: Response):
    
    refresh_token = body.get("refresh_token")
    user_id = body.get("user_id")

    if not refresh_token or not user_id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "message": "All fields are required",
            "metadata": {}
        }

    # 3- CHECK IF THE SESSION IS STILL IN ACTIVE STATUS
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT status, expires_at, id FROM sessions WHERE user_id = %s AND refresh_token = %s", (user_id, refresh_token))
    session = cur.fetchone()

    if session[0] != "ACTIVE":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "success": False,
            "message": "Invalid session",
            "metadata": {}
        }

    if datetime.now() > session[1]:
        cur.execute("""
            UPDATE sessions
            SET status = "Expired"
            WHERE id = %s
        """, (session[2]))
        conn.commit()

        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "success": False,
            "message": "Session expired",
            "metadata": {}
        }   

    # 4- CREATE NEW ACCESS TOKEN
    access_token = create_tokens(user_id)

    # 5- RETURN USER DATA
    cur.execute("SELECT * FROM users WHERE user_id = %s LIMIT 1", (user_id,))
    user_data = cur.fetchone()
    
    
    return {
        "success": True,
        "message": "Welcome Back",
        "metadata": {
            "access_token": access_token,
            "user_id": user_data["id"],
            "email": user_data["email"],
            "username": user_data["username"],
            "status": user_data["status"]
        }
    }

@router.post("/sign-in")
async def function(body: dict, response: Response):

    # 1- GET THE EMAIL AND PASSWORD
    email = body.get("email")
    password = body.get("password") 
    device = body.get("device")
    ip = body.get("ip")

    if not email or not password:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "message": "All fields are required",
            "metadata": {}
        }

    # 2- VERIFY THE LOGIN DATA
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email))
    user = dict(cur.fetchone())
    
    verify = verifyHasedPassword(user["password"], password)

    if not verify:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "success": False,
            "message": "Wrong Password",
            "metadata": {}
        }
    
    # 3- SEND OTP
    otp = str(random.randint(100000, 999999))

    await sendOTP(email, otp)

    # 4- UPDATE USER OTP
    cur.execute("UPDATE users SET otp = %s WHERE email = %s", (otp, email))
    conn.commit()

    return {
        "success": True,
        "message": "OTP sent successfully",
        "metadata": user
    }