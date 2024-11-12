from pydantic import BaseModel
from typing import Optional

class WeatherCreate(BaseModel):
    location: str
    timestamp: Optional[str] = None
    url: Optional[str] = None

class WeatherResponse(BaseModel):
    id: int
    location: str
    timestamp: str
    url: str

    class Config:
        orm_mode = True
