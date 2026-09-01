from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from scripts.schemas import ChatroomResponse, UserResponse, ChatroomCreate
from scripts.db_models import get_session, ChatRoom, ChatroomParticipants
from scripts import oauth

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

