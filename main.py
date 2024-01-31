from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from app.api import authentication, blogs, dashboard
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Include API routers
app.include_router(authentication.router)
app.include_router(blogs.router, prefix="/blogs", tags=["blogs"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])


