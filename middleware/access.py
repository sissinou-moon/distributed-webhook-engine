from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from services.jwt import verify_access_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        if request.url.path.startswith("/auth"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"message": "Unauthorized"})

        token = auth_header.split(" ")[1]
        user_id = verify_access_token(token)

        if user_id == "Exprired":
            return JSONResponse(status_code=401, content={"message": "Token expired"})

        if user_id == "Invalid" or not user_id:
            return JSONResponse(status_code=401, content={"message": "Invalid token"})

        request.state.user_id = user_id

        return await call_next(request)