from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.utils import get_current_user, get_database
from ..models import blog
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

router = APIRouter()

# JWT configurations
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Function to create JWT token
def create_jwt_token(data: dict):
    to_encode = data.copy()
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to get user from MongoDB by username
async def get_user(username: str):
    database = get_database()
    users_collection = database.get_collection("Blogs")
    user_data = await users_collection.find_one({"name": username})
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

@router.post("/register")
async def register_user(user: blog.User):
    # Validate input data using Pydantic
    user_data = user.model_dump()

    # Store the user details in the database (MongoDB)
    # You'll need to use the database dependency and the User model
    database = get_database()
    user_collection = database.get_collection("users")

    # Check if the user already exists
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Store the new user in the database
    result = await user_collection.insert_one(user_data)

    # Check if the insertion was successful
    if result.inserted_id:
        return {"message": "User registered successfully"}

    # Return an error response if the insertion fails
    raise HTTPException(status_code=500, detail="Failed to register user")

@router.put("/update-profile")
async def update_user_profile(
    user: blog.User,
    current_user: blog.User = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    # Validate input data using Pydantic
    user_data = user.model_dump()

    # Update user details in the database
    user_collection = database.get_collection("users")

    # Check if the user exists
    existing_user = await user_collection.find_one({"email": current_user.email})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user details
    update_result = await user_collection.update_one(
        {"email": current_user.email},
        {"$set": user_data}
    )

    # # Update tags of the user
    # update_tag = await user_collection.update_one(
    #     {"email": current_user.email},
    #     {"$set": {"tags": user.tags}}
    # )
    
    # Check if the update was successful
    if update_result.modified_count > 0:
        return {"message": "User profile updated successfully"}

    # Return an error response if the update fails
    raise HTTPException(status_code=500, detail="Failed to update user profile")