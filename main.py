from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from app.api import authentication, blogs, dashboard
from dotenv import load_dotenv
import os


app = FastAPI()

load_dotenv()

# Connect to MongoDB using Motor
database_url = os.getenv("MONGODB_URL")
client = AsyncIOMotorClient(database_url)
database = client.get_database("Blog_Base")

# Include API routers
app.include_router(authentication.router)
app.include_router(blogs.router, prefix="/blogs", tags=["blogs"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# Run the FastAPI app with uvicorn
if __name__ == "__main__":
    import uvicorn
    # uvicorn main:app --reload
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
