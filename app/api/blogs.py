from fastapi import APIRouter, Depends, HTTPException
from app.models.blog import Blog, User
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.utils import get_current_user, get_blog_model, get_database
from typing import List

router = APIRouter()

@router.post("/", response_model=Blog)
async def create_blog(
    blog: Blog,
    current_user: User = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    blog_data = blog.model_dump()

    blog_data["user_id"] = current_user.id

    blog_collection = database.get_collection("Blogs")
    result = await blog_collection.insert_one(blog_data)


    if result.inserted_id:
        return {**blog_data, "id": str(result.inserted_id)}

 
    raise HTTPException(status_code=500, detail="Failed to create blog")

@router.get("/", response_model=list[Blog])
async def get_all_blogs(
    skip: int = 0,
    limit: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_database)
):

    blog_collection = db.get_collection("Blogs")
    blogs = await blog_collection.find().skip(skip).limit(limit).to_list(limit)

    return blogs

@router.get("/{blog_id}", response_model=Blog)
async def get_blog_by_id(
    blog_id: str, db: AsyncIOMotorClient = Depends(get_database)
):
    blog_collection = db.get_collection("Blogs")
    blog = await blog_collection.find_one({"_id": blog_id})
    return blog

@router.put("/{blog_id}", response_model=Blog)
async def update_blog(
    blog_id: str,
    blog: Blog,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    updated_blog_data = blog.model_dump()

    blog_collection = db.get_collection("Blogs")
    existing_blog = await blog_collection.find_one({"_id": blog_id})
    if not existing_blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    if existing_blog.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Unauthorized access")

    update_result = await blog_collection.update_one(
        {"_id": blog_id},
        {"$set": updated_blog_data}
    )
    
    if update_result.modified_count > 0:
        return {**updated_blog_data, "id": blog_id}

    raise HTTPException(status_code=500, detail="Failed to update blog")

@router.delete("/{blog_id}")
async def delete_blog(
    blog_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    blog_collection = db.get_collection("Blogs")
    existing_blog = await blog_collection.find_one({"_id": blog_id})
    if not existing_blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    if existing_blog.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Unauthorized access")

    delete_result = await blog_collection.delete_one({"_id": blog_id})

    if delete_result.deleted_count > 0:
        return {"message": "Blog deleted successfully"}

    raise HTTPException(status_code=500, detail="Failed to delete blog")
