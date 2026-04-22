from middleware.access import AuthMiddleware
from fastapi import FastAPI
from routers import auth

app = FastAPI()

app.add_middleware(AuthMiddleware)

app.include_router(auth.router, prefix="/auth")

@app.get("/state")
def function():
    return {"message": "Hello World"}