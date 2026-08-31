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
EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_extract_token(token: str = Depends(oauth2_scheme),
                 session: Session = Depends(get_session)) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                      detail="Invalid credentials",
                      headers={"WWW-Authenticate": "Bearer"})

    token_data = TokenData(id=payload.get("user_id"))

    return token_data

def get_current_user(token: TokenData = Depends(verify_extract_token),
                     session: Session = Depends(get_session)) -> UserResponse:
    user = session.query(User).where(User.id == token.id).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user