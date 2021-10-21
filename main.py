import asyncio
import logging
from time import sleep

import pytz
import uvicorn
from fastapi import FastAPI, File, Depends
from pydantic import BaseModel
from datetime import datetime, time, timedelta
from fastapi_utils.tasks import repeat_every

from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

import crud
import models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def delete_old_countdown_task(db):
    print('delete_old_countdown_task started')
    now = datetime.now().astimezone(pytz.timezone('Europe/Rome'))
    print('now is: {}'.format(str(now)))
    countdowns = crud.get_countdown_list(db)
    for countdown in countdowns:
        print('countdown start_date {} / end_date {}'.format(countdown.start_date, countdown.end_date))
        if countdown.start_date < now and countdown.end_date < now:
            res = crud.delete_countdown(db, countdown.id)
            if res == 'ok':
                print("Deleted one countdown")
    print("**********************************")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CountDownSchema(BaseModel):
    name: str
    start_date: datetime = datetime.now()
    end_date: datetime


session = Session(engine)


@app.on_event("startup")
@repeat_every(seconds=10)  # 1 hour
async def remove_expired_tokens_task() -> None:
    delete_old_countdown_task(session)


@app.get("/get_countdown/")
def get_countdowns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    countdowns = crud.get_countdown_list(db, skip=skip, limit=limit)
    return countdowns


@app.get("/get_countdown/{id}")
def get_countdown(id: int, db: Session = Depends(get_db)):
    countdowns = crud.get_countdown_detail(db, id=id)
    return countdowns


@app.post("/create_countdown/")
def create_countdown(body: CountDownSchema, db: Session = Depends(get_db)):
    countdown = crud.create_countdown(db, body)
    return countdown


@app.delete("/delete_countdown/")
def delete_countdown(id: int, db: Session = Depends(get_db)):
    countdown = crud.delete_countdown(db, id)
    return countdown


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
