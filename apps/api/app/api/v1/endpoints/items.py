import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.item import ItemCard, ItemDetail
from app.services.home_service import HomeService, to_card, to_detail

router = APIRouter()


@router.get("/item/{item_id}")
async def get_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict[str, ItemDetail | list[ItemCard]]:
    service = HomeService(db)
    item, similar = await service.get_item_detail(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": to_detail(item), "more_like_this": [to_card(i) for i in similar]}
