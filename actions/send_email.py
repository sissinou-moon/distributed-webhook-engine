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

def send_email(to_email: str, subject: str, body: str, from_email: str):
    data = {
        "sender": {"email": from_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": body
    }

    requests.post(url, json=data, headers=headers)