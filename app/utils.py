from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.blog import User, Blog
from main import database

async def get_current_user(data: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    user = await database["Blogs"].find_one({"name": data})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(**user)

def get_database():
    return database

def get_blog_model():
    return Blog