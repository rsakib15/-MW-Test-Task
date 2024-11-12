from sqlalchemy import Column, String, Integer
from ..db import Base

class Weather(Base):
    __tablename__ = 'weather'
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, nullable=True)
    timestamp = Column(String, nullable=True)
    url = Column(String, nullable=True)