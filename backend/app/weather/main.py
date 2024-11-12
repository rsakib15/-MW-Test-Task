from typing import Union, List
from fastapi import FastAPI, HTTPException, BackgroundTasks, status, Depends
import asyncio
import os
from datetime import datetime
import httpx
import json
from backend.app.weather.crud import create_weather
from sqlalchemy.orm import Session
from .db import get_session
from sqlalchemy.ext.asyncio import AsyncSession


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# The endpoint should accept a `GET` request with a `city` query parameter
# Example: http://127.0.0.1:8000/weather?city=dhaka
@app.get("/weather")
async def weather(background_tasks: BackgroundTasks, city:str, session: AsyncSession = Depends(get_session)):
    api_id = "a5cce6e7742008216acb1fb336f95323"
    url = "https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + str(api_id)

    # asynchronously fetch the current weather data from the external API based on the `city` parameter.
    
    async with httpx.AsyncClient() as client:
        try:
            # If the path not exists for storing the data, create a folder to store data
            if not os.path.exists(os.getcwd() + '/weather_data'):
                directory_name = "weather_data"
                os.mkdir(directory_name)


                
            await asyncio.sleep(2) 
            response = await client.get(url)
            current_timestamp = datetime.now().timestamp()

            file_name = f"weather_data/{city}_{current_timestamp}.json"
                
            with open(file_name, "w") as outfile:
                json.dump(response.text, outfile)

            await create_weather(session= Session, city = city, current_timestamp = str(current_timestamp), file_name= file_name)

            return {
                "response": response.json()
            }

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=400, detail=f"Request to external API failed: {str(exc)}"
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error response from external API"
            )