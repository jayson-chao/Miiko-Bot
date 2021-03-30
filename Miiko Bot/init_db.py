# init_db.py
# execute before running bot, use to initialize schema in postgres db

from tortoise import Tortoise, run_async
from tortoise_config import TORTOISE_ORM

async def init():
    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas()

run_async(init())

