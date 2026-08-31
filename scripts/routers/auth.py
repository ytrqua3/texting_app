from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from scripts import oauth
from scripts.db_models import get_session, User
from sqlalchemy.orm import Session
from scripts import utils
from datetime import timedelta
import os
import dotenv
dotenv.load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post('/login')
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
                session: Session = Depends(get_session)):
    user = session.query(User).filter(User.username == user_credentials.username).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user {user_credentials.username} not found")

    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    payload = {"user_id": user.id}
    jwt_token = oauth.create_access_token(payload)
    return {'access_token': jwt_token, 'token_type': 'bearer'}