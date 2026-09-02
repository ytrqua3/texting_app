import uvicorn
from alembic import command
from alembic.config import Config


def run_migrations():
    alembic_cfg = Config("alembic.ini")

    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    #run_migrations()
    uvicorn.run("scripts.app:app", host="0.0.0.0", port=8080, reload=True)