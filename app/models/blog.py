from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: int
    name: str
    email: str
    password: str
    is_active: bool
    tags : List[str] = []

class Blog(BaseModel):
    id: int
    title: str
    body: str
    published: bool
    creator_id: int
    tags : List[str] = []