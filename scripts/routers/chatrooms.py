from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from scripts.schemas import ChatroomResponse
from scripts.db_models import get_session

router = APIRouter(prefix="/chatrooms", tags=["chatrooms"])

@router.get("/{id}")
async def get_chatroom(id: int,
                       session: Session = Depends(get_session),
                       limit: int = 10) -> ChatroomResponse:
    pass
