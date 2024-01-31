from fastapi import APIRouter, Depends, HTTPException
from app.models.blog import User, Blog
from app.utils import get_current_user, get_blog_model, get_database
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.get("/", response_model=List[Blog])
async def get_dashboard_blogs(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    followed_tags = current_user.tags

    blog_collection = database.get_collection("Blogs")
    query = {"tags": {"$in": followed_tags}}
    blog_collection.create_index([("tags", -1)])
    
    blogs = await blog_collection.find(query).skip(skip).limit(limit).to_list(limit)

    return blogs