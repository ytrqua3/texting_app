from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from scripts.schemas import UserCreate, UserResponse, TokenData
from sqlalchemy.orm import Session
from sqlalchemy import select
from scripts.db_models import get_session, User
from scripts.utils import hash_password
from scripts.oauth import get_current_user, verify_extract_token

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate,
                      session: Session = Depends(get_session)) -> UserResponse:
    new_user = User(**user.model_dump())
    new_user.password = hash_password(user.password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_user(user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return user

@router.get("/my_chatrooms")
async def get_my_chatroom(current_user: UserResponse = Depends(get_current_user),
                          session: Session = Depends(get_session)):
    result = session.scalars(select(User).where(User.id == current_user.id)).one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    chatrooms = result.chatrooms
    return chatrooms