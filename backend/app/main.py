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

def get_city_and_timestamp(file_name):
    print(file_name)
    try:
        city, timestamp_str = file_name.rsplit('_', 1)
        print(city, timestamp)
        timestamp = float(timestamp_str.split('.')[0])
        return city, timestamp
    except ValueError:
        raise ValueError("Invalid file name format. Expected format: city_timestamp.json")

def check_file_exists(city):
    files = [f for f in os.listdir(os.getcwd() + '/weather_data') if f.startswith(city)]
    latest_file = max(files, key=lambda f: get_city_and_timestamp(f)[1])
    print(latest_file)
    return True if len(files) > 0 else False
    
def get_latest_file(file_name):
    try:
        city, timestamp_str = file_name.rsplit('_', 1)
        timestamp = float(timestamp_str.split('.')[0])
        return city, timestamp
    except ValueError:
        raise ValueError("Invalid file name format. Expected format: city_timestamp.json")
        

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
            current_timestamp = datetime.now().timestamp()

            file_name = f"weather_data/{city}_{current_timestamp}.json"
            
            # Store each fetched weather response as a JSON file in an S3 bucket or a loca
            with open(file_name, "w") as outfile:
                json.dump(response.text, outfile)

            await create_weather(Sessiondb, city, str(current_timestamp), file_name)

            # Caching with S3/Local Equivalent
            if check_file_exists(city):
                file = get_latest_file(city)
                print(file)

                

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
        





#         def get_city_and_timestamp(file_name):
# try:
# city, timestamp_str = file_name.rsplit('_', 1)
# timestamp = float(timestamp_str.split('.')[0])
# return city, timestamp
# except ValueError:
# raise ValueError("Invalid file name format. Expected format: city_timestamp.json")

# def check_file_exists(city, directory='.'):
# files = [f for f in os.listdir(directory) if f.startswith(city)]
# return files

# def get_latest_file(files):
# latest_file = max(files, key=lambda f: get_city_and_timestamp(f)[1])
# return latest_file

# def is_recent(timestamp, minutes=5):
# file_time = datetime.fromtimestamp(timestamp)
# return datetime.now() - file_time < timedelta(minutes=minutes)

# def main(file_name, directory='.'):
# city, timestamp = get_city_and_timestamp(file_name)
# files = check_file_exists(city, directory)

# if files:
# latest_file = get_latest_file(files)
# latest_timestamp = get_city_and_timestamp(latest_file)[1]

# if is_recent(latest_timestamp):
# with open(os.path.join(directory, latest_file), 'r') as f:
# data = f.read()
# return data
# else:
# return "No recent file found."
# else:
# return "No file found for the given city."

# # Example usage
# file_name = "dhaka_1731396873.266913.json"
# print(main(file_name))