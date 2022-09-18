import json
import logging
import os
from os import environ

from dotenv import load_dotenv
from nextcord import Intents
from nextcord.ext.commands import Bot
from nextcord.ext.commands.errors import ExtensionError


class ColourFormatter(logging.Formatter):
    PREFIX = "\033["
    BASE = "%(asctime)s : %(name)-25s : %(levelname)-8s : %(message)s"
    RESET = f"{PREFIX}0m"

    COLOURS = {
        logging.DEBUG: "32m",
        logging.INFO: "34m",
        logging.WARNING: "33m",
        logging.ERROR: "31m",
        logging.CRITICAL: "31m"
    }

    def format(self, record):
        colour = self.COLOURS.get(record.levelno)
        fmt = f"{self.PREFIX}{1 if record.name.endswith(environ['LOGGER']) else 0};{colour}{self.BASE}{self.RESET}"
        formatter = logging.Formatter(fmt)
        return formatter.format(record)


class DiscordBotName(Bot):
    def __init__(self, logger: logging.Logger, config_path: str, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger

        self.config_path = config_path
        self.config = {}
        self.load_config()

        self.owner_id = self.config.get("owner_id")

    def load_config(self) -> bool:
        if not os.path.isfile(self.config_path) and self.config_path.endswith(".json"):
            self.logger.debug("Bot config is not a JSON file")
            return False
        with open(self.config_path, "r") as file:
            self.config = json.load(file)
        return True

    def load_all_extensions(self) -> list[str]:
        extensions_path = self.config.get("extensions_path")
        if not extensions_path:
            self.logger.debug("'extensions_path' is not specified in the bot config")
            return []
        elif not os.path.isdir(extensions_path):
            self.logger.debug("'extensions_path' is not a directory")
            return []

        failed_extensions = []
        for python_file in list(filter(lambda s: (s.endswith(".py")), os.listdir(extensions_path))):
            name = python_file.replace(".py", "")
            extension = f"{extensions_path}.{name}"
            try:
                self.load_extension(extension)
            except ExtensionError as error:
                failed_extensions.append(extension)
                self.logger.error(error)
        return failed_extensions

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        self.load_all_extensions()
        await super().start(token, reconnect=reconnect)


if __name__ == '__main__':
    load_dotenv()

    # Configure nextcord logger
    nextcord = logging.getLogger("nextcord")
    nextcord.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(ColourFormatter())
    nextcord.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename=environ["LOG_PATH"], encoding='utf-8', mode='w')
    file_handler.setFormatter(logging.Formatter(ColourFormatter.BASE))
    nextcord.addHandler(file_handler)

    # Create bot logger
    bot_logger = nextcord.getChild(environ['LOGGER'])
    bot_logger.setLevel(logging.DEBUG)

    # Create bot client
    intents = Intents.default()
    bot = DiscordBotName(logger=bot_logger, config_path=environ["CONFIG_PATH"], intents=intents)

    # Run client
    bot.run(environ["TOKEN"])
