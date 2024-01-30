from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from motor.motor_asyncio import AsyncIOMotorClient
from ..models import blog
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

router = APIRouter()

# JWT configurations
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MongoDB configurations
database_url = os.getenv("MONGODB_URL")
client = AsyncIOMotorClient(database_url)
database = client.get_database("Blog_base")
users_collection = database.get_collection("Blogs")

# Function to create JWT token
def create_jwt_token(data: dict):
    to_encode = data.copy()
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to get user from MongoDB by username
async def get_user(username: str):
    user_data = await users_collection.find_one({"username": username})
    if user_data:
        return blog.User(**user_data)
    return None

# OAuth2PasswordBearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to verify credentials and create JWT token
async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if user and password == user["password"]:
        return user
    return None

# Endpoint to get JWT token
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordBearer = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = {"sub": user["username"]}
    return {"access_token": create_jwt_token(token_data), "token_type": "bearer"}
