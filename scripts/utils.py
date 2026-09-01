import bcrypt
from sqlalchemy.orm import Session
from scripts.db_models import ChatroomParticipants
from scripts.schemas import UserResponse
from fastapi import HTTPException, status
from sqlalchemy import select

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed_password) -> bool:
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        return True
    else:
        return False

def check_participant_in_chatroom(session: Session,
                                  current_user: UserResponse,
                                  id):
    # check if chatroom exists and if user is in chatroom and if user is chatroom's admin
    result = session.execute(select(ChatroomParticipants.is_admin).filter(ChatroomParticipants.user_id == current_user.id,ChatroomParticipants.chatroom_id == id)).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User is not in chatroom {id} or chatroom {id} does not exist")
    return result

def check_is_admin(session: Session,
                current_user: UserResponse,
                id):
    result = check_participant_in_chatroom(session, current_user, id)

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"User is not an admin of chatroom {id}")