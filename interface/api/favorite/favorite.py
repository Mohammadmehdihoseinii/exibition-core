from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from src.database.db_manager import db_manager
from src.database.models import FavoriteTypeEnum

router = APIRouter(prefix="/favorites", tags=["Favorites"])

# -------------------- Schemas --------------------
class FavoriteCreateSchema(BaseModel):
    favorite_type: FavoriteTypeEnum
    target_id: int

class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    favorite_type: str
    target_id: int

class FavoriteCountResponse(BaseModel):
    favorite_type: str
    target_id: int
    count: int

# -------------------- API Endpoints --------------------
@router.post("/", response_model=FavoriteResponse)
def add_favorite(user_id: int, req: FavoriteCreateSchema):
    favorite = db_manager.favorite.add_favorite(
        user_id=user_id,
        favorite_type=req.favorite_type,
        target_id=req.target_id
    )
    return FavoriteResponse(
        id=favorite.id,
        user_id=favorite.user_id,
        favorite_type=favorite.favorite_type.value,
        target_id=favorite.target_id
    )

@router.delete("/", response_model=dict)
def remove_favorite(user_id: int, favorite_type: FavoriteTypeEnum = Query(...), target_id: int = Query(...)):
    removed = db_manager.favorite.remove_favorite(
        user_id=user_id,
        favorite_type=favorite_type,
        target_id=target_id
    )
    return {"removed": removed}

@router.get("/user", response_model=List[FavoriteResponse])
def get_user_favorites(user_id: int, favorite_type: Optional[FavoriteTypeEnum] = None):
    favorites = db_manager.favorite.get_user_favorites(user_id=user_id, favorite_type=favorite_type)
    return [
        FavoriteResponse(
            id=f.id,
            user_id=f.user_id,
            favorite_type=f.favorite_type.value,
            target_id=f.target_id
        ) for f in favorites
    ]

@router.get("/count", response_model=FavoriteCountResponse)
def count_favorites(favorite_type: FavoriteTypeEnum = Query(...), target_id: int = Query(...)):
    count = db_manager.favorite.count_favorites(favorite_type=favorite_type, target_id=target_id)
    return FavoriteCountResponse(
        favorite_type=favorite_type.value,
        target_id=target_id,
        count=count
    )
