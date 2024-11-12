import asyncio
from ..db import engine, Base

async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

asyncio.run(init_db)