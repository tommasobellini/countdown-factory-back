from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.orm import Session

import models


class CountDownSchema(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime


def get_countdown_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Countdown).offset(skip).limit(limit).all()


def get_countdown_detail(db: Session, id: int):
    return db.query(models.Countdown).filter(models.Countdown.id == id).first()


def create_countdown(db: Session, countdown: CountDownSchema):
    db_countdown = models.Countdown(**countdown.dict())
    db.add(db_countdown)
    db.commit()
    db.refresh(db_countdown)
    return db_countdown
