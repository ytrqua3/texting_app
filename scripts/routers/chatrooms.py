from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from scripts.schemas import ChatroomResponse, UserResponse, ChatroomCreate, MessageResponse, ChatroomParticipantResponse
from scripts.db_models import get_session, ChatRoom, ChatroomParticipants, User, Message
from scripts import oauth
from scripts.utils import check_is_admin, check_participant_in_chatroom

router = APIRouter(prefix="/chatrooms", tags=["chatrooms"])

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


@router.get("/participant/{id}")
async def get_chatroom_participants(id: int,
                                    session: Session = Depends(get_session),
                                    current_user: UserResponse = Depends(oauth.get_current_user)) -> list[ChatroomParticipantResponse]:
    check_participant_in_chatroom(session, current_user, id)

    result = session.query(ChatroomParticipants).filter(ChatroomParticipants.chatroom_id == id).all()

    return result

@router.post("/participant/{id}", status_code=status.HTTP_201_CREATED)
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

@router.delete("/participant/{id}", status_code=status.HTTP_204_NO_CONTENT)
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

    admins = session.query(ChatroomParticipants).filter(ChatroomParticipants.is_admin == True, ChatroomParticipants.chatroom_id == id).all()
    if not admins or user_id not in admins:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found as admin")

    if len(admins) == 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user is last admin in the group")

    for admin in admins:
        if admin.user_id == user_id:
            admin.is_admin = False
            session.commit()
            return

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def read_latest_messages(id: int,
                        limit: int = 100,
                        session: Session = Depends(get_session),
                        current_user: UserResponse = Depends(oauth.get_current_user)) -> list[MessageResponse]:
    check_participant_in_chatroom(session, current_user, id)

    result = session.query(Message.content, Message.owner_id, Message.created_at).where(Message.chatroom_id == id).order_by(Message.created_at.desc()).limit(limit).all()
    return result

@router.post("/{id}", status_code=status.HTTP_201_CREATED)
async def send_message(id: int,
                       message: str,
                       session: Session = Depends(get_session),
                       current_user: UserResponse = Depends(oauth.get_current_user)) -> MessageResponse:
    check_participant_in_chatroom(session, current_user, id)

    new_message = Message(content=message, chatroom_id = id, owner_id = current_user.id)

    session.add(new_message)
    session.commit()
    session.refresh(new_message)
    return new_message