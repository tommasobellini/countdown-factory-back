from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from database import Base


class Countdown(Base):
    __tablename__ = 'countdown'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)
    start_date = Column(DateTime, index=True)
    end_date = Column(DateTime, index=True)
