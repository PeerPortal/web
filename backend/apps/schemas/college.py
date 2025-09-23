from typing import List, Optional
from pydantic import BaseModel

class CollegeImage(BaseModel):
    id: Optional[int] = None
    image_url: str
    caption: Optional[str] = None
    sort_order: int = 0

class CollegeBase(BaseModel):
    name: str
    location: str
    type: str
    description: str

class CollegeCreate(CollegeBase):
    images: List[CollegeImage] = []

class College(CollegeBase):
    id: int
    images: List[CollegeImage] = []

    class Config:
        orm_mode = True
