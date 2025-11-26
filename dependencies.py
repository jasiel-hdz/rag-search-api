from fastapi import Depends, HTTPException, status
from database import sessionLocal
from config import get_settings

settings = get_settings()


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
