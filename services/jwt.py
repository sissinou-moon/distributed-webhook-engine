import jwt, datetime, uuid, bcrypt
from dotenv import load_dotenv
import os
from services.password import hashPassword

load_dotenv()

SECRET = os.getenv("SECRET")

def create_tokens(user_id):
    access = jwt.encode({
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET, algorithm="HS256")

    raw_refresh = str(uuid.uuid4())

    refresh_hash = hashPassword(raw_refresh)

    return access, raw_refresh

def verify_access_token(token):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload["sub"]  # user_id
    except jwt.ExpiredSignatureError:
        return "Exprired"  # expired
    except jwt.InvalidTokenError:
        return "Invalid"  # invalid