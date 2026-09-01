from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from scripts.schemas import ChatroomResponse, UserResponse, ChatroomCreate
from scripts.db_models import get_session, ChatRoom, ChatroomParticipants, User
from scripts import oauth

router = APIRouter(prefix="/chatrooms", tags=["chatrooms"])

def check_is_admin(session: Session,
                current_user: UserResponse,
                id):
    result = check_participant_in_chatroom(session, current_user, id)

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"User is not an admin of chatroom {id}")

def check_participant_in_chatroom(session: Session,
                                  current_user: UserResponse,
                                  id):
    # check if chatroom exists and if user is in chatroom and if user is chatroom's admin
    result = session.query(ChatroomParticipants.is_admin).filter(ChatroomParticipants.user_id == current_user.id,
                                                                 ChatroomParticipants.chatroom_id == id).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User is not in chatroom {id} or chatroom {id} does not exist")
    return result

@router.post("")
async def create_chatroom(chatroom: ChatroomCreate,
                          session: Session = Depends(get_session),
                          user: UserResponse = Depends(oauth.get_current_user)) -> ChatroomResponse:
    new_chat = ChatRoom(**chatroom.model_dump())
    session.add(new_chat)
    session.commit()
    session.refresh(new_chat)

    new_chat_participant = ChatroomParticipants(user_id=user.id,
                                                chatroom_id = new_chat.id,
                                                is_admin = True)
    session.add(new_chat_participant)
    session.commit()
    return new_chat

@router.get("/")
async def get_chatrooms(session: Session = Depends(get_session),
                        current_user: UserResponse = Depends(oauth.get_current_user)):
    result = session.scalars(User).where(User.id == current_user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    chatrooms = result.chatrooms
    print(chatrooms)
    return chatrooms

@router.post("/add_participant/{id}", status_code=status.HTTP_201_CREATED)
async def add_chatroom_participant(id: int,
                                   user_id: int,
                                   session: Session = Depends(get_session),
                                   current_user: UserResponse = Depends(oauth.get_current_user)):
    check_is_admin(session, current_user, id)

    # add users to chatroom_participants
    user = session.query(User).filter(User.id == user_id).one_or_none()

    # check if the user exists
    if not user:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} does not exist")

    # add to chatroom_participants table
    new_participant = ChatroomParticipants(user_id=user.id,
                                               chatroom_id = id)
    session.add(new_participant)
    session.commit()
    return

@router.delete("/remove_participant/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_chatroom_participant(id: int,
                                   user_id: int,
                                   session: Session = Depends(get_session),
                                   current_user: UserResponse = Depends(oauth.get_current_user)):
    check_is_admin(session, current_user, id)
    chatroom_association = session.query(ChatroomParticipants) .filter(ChatroomParticipants.user_id == user_id, ChatroomParticipants.chatroom_id == id).one_or_none()
    if not chatroom_association:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not in chatroom")

    session.delete(chatroom_association)
    session.commit()

@router.put("/make_admin/{id}")
async def make_admin(id: int,
                     user_id: int,
                     session: Session = Depends(get_session),
                     current_user: UserResponse = Depends(oauth.get_current_user)):
    check_is_admin(session, current_user, id)

    user = session.query(ChatroomParticipants).filter(ChatroomParticipants.user_id == user_id, ChatroomParticipants.chatroom_id == id).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    user.is_admin = True
    session.commit()

@router.put("/remove_admin/{id}")
async def remove_admin(id: int,
                     user_id: int,
                     session: Session = Depends(get_session),
                     current_user: UserResponse = Depends(oauth.get_current_user)):
    check_is_admin(session, current_user, id)

    user = session.query(ChatroomParticipants).filter(ChatroomParticipants.user_id == user_id, ChatroomParticipants.chatroom_id == id).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    user.is_admin = False
    session.commit()

