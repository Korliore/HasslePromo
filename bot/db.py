import asyncpg
from bot.config import DATABASE_URL

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def close(self):
        await self.pool.close()

    async def execute(self, *args, **kwargs):
        async with self.pool.acquire() as conn:
            return await conn.execute(*args, **kwargs)

    async def fetch(self, *args, **kwargs):
        async with self.pool.acquire() as conn:
            return await conn.fetch(*args, **kwargs)

    async def fetchrow(self, *args, **kwargs):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(*args, **kwargs)

db = Database()