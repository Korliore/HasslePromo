import logging

from redis.client import Redis
from bot.config import REDIS_HOST, REDIS_PORT, REDIS_DB 

logger = logging.getLogger("uvicorn")

r = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
)
