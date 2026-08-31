from fastapi import FastAPI
import dotenv
dotenv.load_dotenv()
from db_models import create_all_tables

app = FastAPI()

create_all_tables()

@app.get("/")
async def root():
    return {"message": "Welcome to my texting app"}