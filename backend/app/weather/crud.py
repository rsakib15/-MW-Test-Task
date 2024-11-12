from ..models.weather import Weather as weather_model
from sqlalchemy.ext.asyncio import AsyncSession

async def create_weather(session: AsyncSession, city: str, current_timestamp: str, file_name: str):
    new_weather = weather_model(location=city, timestamp= current_timestamp, url = file_name)
    session.add(new_weather)
    await session.commit()
    await session.refresh(new_weather)
    return new_weather