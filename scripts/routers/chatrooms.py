from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from scripts.schemas import ChatroomResponse, UserResponse, ChatroomCreate
from scripts.db_models import get_session, ChatRoom, ChatroomParticipants, User
from scripts import oauth

router = APIRouter(prefix="/chatrooms", tags=["chatrooms"])

def check_admin(session: Session,
                current_user: User,
                id):
    # check if chatroom exists and if user is in chatroom and if user is chatroom's admin
    result = session.query(ChatroomParticipants.is_admin).filter(ChatroomParticipants.user_id == current_user.id,
                                                                 ChatroomParticipants.chatroom_id == id).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User is not in chatroom {id} or chatroom {id} does not exist")

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"User is not an admin of chatroom {id}")

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

@router.post("/{id}/add_participants", status_code=status.HTTP_201_CREATED)
async def add_chatroom_participant(id: int,
                                   user_ids: list[int],
                                   session: Session = Depends(get_session),
                                   current_user: User = Depends(oauth.get_current_user)):
    check_admin(session, current_user, id)

    # add users to chatroom_participants
    for user_id in user_ids:
        # check if the user exists
        user = session.query(User).filter(User.id == user_id).one_or_none()
        if not user:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {id} does not exist")

        # add to chatroom_participants table
        new_participant = ChatroomParticipants(user_id=user.id,
                                               chatroom_id = id)
        session.add(new_participant)

    session.commit()

    return

@router.put("/{id}/make_admin")
async def make_admin(id: int,
                     user_ids: list[int],
                     session: Session = Depends(get_session),
                     current_user: User = Depends(oauth.get_current_user)):
    check_admin(session, current_user, id)

    