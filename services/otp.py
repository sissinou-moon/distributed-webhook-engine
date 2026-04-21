import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://api.brevo.com/v3/smtp/email"

headers = {
    "accept": "application/json",
    "api-key": os.getenv("BREVO_APIKEY"),
    "content-type": "application/json"
}

async def sendOTP(email: str, otp: str):
    data = {
        "sender": {"email": "playwithyas@gmail.com"},
        "to": [{"email": email}],
        "subject": "Your OTP",
        "htmlContent": f"<h1>Your OTP: {otp}</h1>"
    }

    requests.post(url, json=data, headers=headers)