from fastapi import FastAPI
import dotenv
dotenv.load_dotenv()
from .db_models import create_all_tables
from scripts.routers import users, auth, chatrooms

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(chatrooms.router)

create_all_tables()

@app.get("/")
async def root():
    return {"message": "Welcome to my texting app"}