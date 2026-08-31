from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
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

def create_all_tables():
    Base.metadata.create_all(engine)

def get_session() -> Session:
    with Session(engine) as session:
        yield session