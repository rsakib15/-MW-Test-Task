from typing import Union, List
from fastapi import FastAPI, HTTPException, BackgroundTasks, status, Depends
import asyncio
import os
from datetime import datetime
import httpx
import json

from .db import engine, Base
from sqlalchemy.orm import Session
from .db import get_session
from .models.weather import Weather as weather_model
from sqlalchemy.ext.asyncio import AsyncSession
from .weather.crud import create_weather

app = FastAPI()

@app.get("/")
def read_root():
    return {"response": "Hello World"}

def get_latest_file_with_city(city_name):
    files_list = [f for f in os.listdir(os.getcwd() + '/weather_data') if f.startswith(city_name)]

    latest_file = None
    latest_timestamp = None
    
    for file_path in files_list:
        file_name = os.path.basename(file_path)
        
        if city_name in file_name:
            try:
                timestamp_str = ''.join(filter(str.isdigit, file_name.split(city_name)[-1]))
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')

                if latest_timestamp is None or timestamp > latest_timestamp:
                    
                    if latest_timestamp is not None:
                        time_difference = abs(timestamp - latest_timestamp)
                        if time_difference > 300:
                            continue

                    latest_file = file_path
                    latest_timestamp = timestamp
            except (ValueError, IndexError):
                pass

    return latest_file

        

@app.get("/weather")
async def weather(background_tasks: BackgroundTasks, city:str, Sessiondb: Session = Depends(get_session)):
    api_id = "a5cce6e7742008216acb1fb336f95323"
    url = "https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + str(api_id)

    async with httpx.AsyncClient() as client:
        try:
            if not os.path.exists(os.getcwd() + '/weather_data'):
                directory_name = "weather_data"
                os.mkdir(directory_name)
                
            await asyncio.sleep(2) 
            response = await client.get(url)
            current_timestamp = datetime.now()

            file_name = f"weather_data/{city}_{current_timestamp}.json"
            
            # Store each fetched weather response as a JSON file in an S3 bucket or a loca
            with open(file_name, "w") as outfile:
                json.dump(response.text, outfile)

            # await create_weather(Sessiondb, city, str(current_timestamp), file_name)
            latest_file = get_latest_file_with_city(city)
            if latest_file:
                with open(f"weather_data/{latest_file}.json", r) as file:
                    data = file.load()
                    return {
                        "status_code": "200",
                        "messsge": {
                            "location": data["name"],
                            "temparature": data["main"]["temp"]

                        }
                    }

            response = response.json()
            if response['cod'] == 200:
                return {
                    "status_code": "200",
                    "messsge": {
                        "location": response["name"],
                        "temparature": response["main"]["temp"]

                    }
                }
            elif response['cod'] == '404':
                return {
                    "status_code": "404",
                    "message":"city not found"
                }
            else:
                return {
                    "status_code": "500",
                    "message":"Something Went wrong"
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
        