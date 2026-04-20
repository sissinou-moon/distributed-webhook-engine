from fastapi import FastAPI

app = FastAPI()

@app.get("/state")
def function():
    return {"message": "Hello World"}