from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GameWeather(Base):
    __tablename__ = "game_weather"

    id = Column(Integer, primary_key=True)
    temperature = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    conditions = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
