import os

import pytz
import uvicorn
from fastapi import FastAPI, File, Depends, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.params import Form
from pydantic import BaseModel
from datetime import datetime, time, timedelta
from fastapi_utils.tasks import repeat_every

from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

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
    try:
        print('delete_old_countdown_task started')
        now = datetime.now().astimezone(pytz.timezone('Europe/Rome'))
        print('now is: {}'.format(str(now)))
        countdowns = crud.get_countdown_list(db)
        for countdown in countdowns:
            print('countdown start_date {} / end_date {}'.format(countdown.start_date.astimezone(),
                                                                 countdown.end_date.astimezone()))
            print(countdown.start_date.astimezone() < now)
            print(countdown.end_date.astimezone() < now)
            if countdown.start_date.astimezone() < now and countdown.end_date.astimezone() < now:
                print('passing')
                res = crud.delete_countdown(db, countdown.id)
                print(res)
                if res == 'ok':
                    print("Deleted one countdown")
        print("**********************************")
    except Exception as e:
        print(e.__str__())


app = FastAPI()
app.mount("/rewards", StaticFiles(directory="rewards"), name="rewards")
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
    reward: str = None


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
def create_countdown(name: str = Form(...), start_date: datetime = Form(...), end_date: datetime = Form(...), reward: UploadFile = File(...), db: Session = Depends(get_db)):
    print(reward.file)
    try:
        os.mkdir("rewards")
        print(os.getcwd())
    except Exception as e:
        print(e)
    short_name = "/rewards/" + reward.filename.replace(" ", "-")
    file_name = os.getcwd() + short_name
    with open(file_name, 'wb+') as f:
        f.write(reward.file.read())
        f.close()
    if os.environ.get("PROD"):
        full_name_url = "https://countdown-factory.herokuapp.com" + short_name
    else:
        full_name_url = "http://localhost:8000" + short_name
    countdown = CountDownSchema(
        name=name,
        start_date=start_date,
        end_date=end_date,
        reward=full_name_url
    )
    countdown = crud.create_countdown(db, countdown)
    return countdown


@app.delete("/delete_countdown/")
def delete_countdown(id: int, db: Session = Depends(get_db)):
    countdown = crud.delete_countdown(db, id)
    return countdown


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
