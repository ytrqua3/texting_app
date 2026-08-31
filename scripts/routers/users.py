from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from scripts.schemas import UserCreate, UserResponse
from sqlalchemy.orm import Session
from scripts.db_models import get_session, User
from scripts.utils import hash_password, verify_password
from scripts.oauth import get_current_user

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