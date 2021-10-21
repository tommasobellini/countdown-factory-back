from typing import Optional

import uvicorn
from fastapi import FastAPI, File, Depends
from pydantic import BaseModel
from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

import crud
import models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



class CountDownSchema(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime


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
    # return {
    #     "name": "First countdown of the year",
    #     "start_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    #     "end_date": (datetime.now() + timedelta(hours=2)).strftime("%d-%m-%Y %H:%M:%S"),
    # }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)