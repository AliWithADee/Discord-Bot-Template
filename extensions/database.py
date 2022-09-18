from os import environ

from aiomysql import Pool, create_pool
from nextcord.ext.commands import Cog

from bot import DiscordBotName


class DatabaseCog(Cog):
    def __init__(self, bot: DiscordBotName, pool: Pool):
        self.bot = bot
        self.pool = pool

    # DATABASE METHODS


async def setup(bot: DiscordBotName):
    bot.logger.info("Loading Database extension...")

    bot.logger.info("Connecting to database...")
    pool: Pool = await create_pool(
        host=environ["DB_HOST"],
        port=int(environ["DB_PORT"]),
        user=environ["DB_USER"],
        password=environ["DB_PASSWORD"],
        db=environ["DB_DATABASE"],
        autocommit=True,
        loop=bot.loop
    )

    bot.add_cog(DatabaseCog(bot, pool))
