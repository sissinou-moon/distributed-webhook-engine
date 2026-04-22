from middleware.access import AuthMiddleware
from fastapi import FastAPI
from routers import auth
from routers import webhook
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(webhook.router, prefix="/webhook")

@app.get("/state")
def function():
    return {"message": "Hello World"}