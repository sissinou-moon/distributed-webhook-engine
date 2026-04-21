from fastapi import FastAPI
from routers import auth

app = FastAPI()

app.include_router(auth.router, prefix="/auth")

@app.get("/state")
def function():
    return {"message": "Hello World"}