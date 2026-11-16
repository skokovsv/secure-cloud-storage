from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import engine, get_db
from app.models import User
from app.schemas import UserCreate, UserOut
from app.security import hash_password

app = FastAPI(title="Secure Cloud Storage")

DbSession = Annotated[Session, Depends(get_db)]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: DbSession):
    user = User(username=data.username, password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
        ) from None
    db.refresh(user)
    return user
