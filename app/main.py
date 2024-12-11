from fastapi import Depends, FastAPI, Request
import uvicorn
import logging
import time
from fastapi.middleware.cors import CORSMiddleware
import json
# from app.resources.composite_resource import check_authorization
from app.routers import composite
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Explicitly allow methods
    allow_headers=["*"],  # Explicitly allow headers
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Simulated database
fake_users_db = {
    "ct3008": {"user_id": 1, "username": "ct3008", "password": "password"}
}

def verify_token(token: str = Depends(oauth2_scheme)):
    print("Verifying token: ", token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("payload: ", payload)
        user_id: int = payload.get("user_id")
        print("User_id verify: ", user_id)
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:4200",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
        },
    )

@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    print("request: ", request.headers)
    if request.method == "OPTIONS":
        return await call_next(request)
    path = request.url.path
    print("path: ", path)
    if path.startswith("/composite"):
        print("start with composite")
        token = request.headers.get("Authorization")
        print("token middleware: ", token)
        if token and token.startswith("Bearer "):
            print("bearer")
            token = token[7:]
            print("new token: ", token)
            user_id = verify_token(token)  # Remove "Bearer " prefix
            request.state.user_id = user_id
        else:
            raise HTTPException(status_code=401, detail="Authentication required")
    print("Out of here")
    response = await call_next(request)
    return response

# Middleware to log requests before and after
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")

    # Log before the request is processed
    start_time = time.time()

    # Call the next process in the pipeline
    response = await call_next(request)

    # Log after the request is processed
    process_time = time.time() - start_time
    logger.info(f"Response status: {response.status_code} | Time: {process_time:.4f}s")

    return response

composite_router = composite.router

# Apply the authorization check to all routes under /composite
# composite_router = APIRouter(
#     dependencies=[Depends(check_authorization)]  # Apply authorization check globally for all routes
# )
app.include_router(composite.router)

user_context: ContextVar[dict] = ContextVar("user_context")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# class AuthMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         auth_header = request.headers.get("Authorization")
#         if auth_header and auth_header.startswith("Bearer "):
#             token = auth_header.split(" ")[1]
#             try:
#                 payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#                 user_context.set(payload)  # Store user info in context
#             except JWTError:
#                 pass
#         return await call_next(request)

# app.add_middleware(AuthMiddleware)



@app.get("/")
async def root():
    return {"message": "Hello Composite Applications!"}

with open("openapi.json", "w") as f:
    json.dump(app.openapi(), f)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5006)



