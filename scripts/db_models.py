from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import ForeignKey
import datetime
from sqlalchemy import func
from sqlalchemy import create_engine
import os

engine = create_engine(os.getenv("DATABASE_URL"))

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

class ChatRoom(Base):
    __tablename__ = "chatrooms"

    id: Mapped[int] = mapped_column(primary_key=True)

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    chatroom_id: Mapped[int] = mapped_column(ForeignKey("chatrooms.id"))
    content: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

class ChatroomParticipants(Base):
    __tablename__ = "chatroom_participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    chatroom_id: Mapped[int] = mapped_column(ForeignKey("chatrooms.id"))
    joined_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

def create_all_tables():
    Base.metadata.create_all(engine)

def get_session() -> Session:
    with Session(engine) as session:
        yield session