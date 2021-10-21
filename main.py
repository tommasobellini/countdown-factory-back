from typing import Optional

import uvicorn
from fastapi import FastAPI, File
from pydantic import BaseModel
from datetime import datetime, time, timedelta

from starlette.middleware.cors import CORSMiddleware

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
    start_date: datetime
    end_date: datetime


@app.get("/get_countdown/")
def get_countdown():
    return {
        "name": "First countdown of the year",
        "start_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "end_date": (datetime.now() + timedelta(hours=2)).strftime("%d-%m-%Y %H:%M:%S"),
    }


@app.post("/create_countdown/")
def create_countdown(body: CountDownSchema):
    return {
        "name": "First countdown of the year",
        "start_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "end_date": (datetime.now() + timedelta(hours=2)).strftime("%d-%m-%Y %H:%M:%S"),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)