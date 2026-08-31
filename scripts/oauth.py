import jwt
from datetime import datetime, timedelta, timezone
import os
import dotenv
from scripts.schemas import TokenData

from scripts.schemas import UserResponse

dotenv.load_dotenv()
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from scripts.db_models import get_session, User

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_extract_token(token: str = Depends(oauth2_scheme),
                 session: Session = Depends(get_session)) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get("id")

    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                      detail="Invalid credentials",
                      headers={"WWW-Authenticate": "Bearer"})

    result = session.query(User).filter(User.id == user_id).one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    token_data = TokenData(id=user_id)

    return token_data

def get_current_user(token: str = Depends(oauth2_scheme),
                     session: Session = Depends(get_session)) -> UserResponse:
    user_token = verify_extract_token()
    user = session.query(User).where(User.id == user_token.id).one_or_none()
    return user