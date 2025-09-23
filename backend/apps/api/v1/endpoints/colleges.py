from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from apps.schemas.college import College, CollegeCreate

router = APIRouter()

# 假数据存储
FAKE_COLLEGES = [
    College(
        id=1,
        name="清华大学",
        location="北京",
        type="综合类",
        description="中国著名高等学府...",
        images=[
            {"id": 1, "image_url": "https://example.com/xxx.jpg", "caption": "主楼", "sort_order": 0}
        ]
    ),
    College(
        id=2,
        name="复旦大学",
        location="上海",
        type="综合类",
        description="中国著名高等学府...",
        images=[]
    )
]

@router.get("/colleges", response_model=List[College])
def get_colleges():
    return FAKE_COLLEGES

@router.post("/colleges", response_model=College, status_code=status.HTTP_201_CREATED)
def create_college(college: CollegeCreate):
    new_id = max([c.id for c in FAKE_COLLEGES], default=0) + 1
    new_college = College(id=new_id, **college.dict())
    FAKE_COLLEGES.append(new_college)
    return new_college

@router.get("/colleges/{college_id}", response_model=College)
def get_college(college_id: int):
    for c in FAKE_COLLEGES:
        if c.id == college_id:
            return c
    raise HTTPException(status_code=404, detail="College not found")