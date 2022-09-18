from nextcord import Interaction, Embed, Colour
from nextcord.ext.application_checks import ApplicationNotOwner

from bot import DiscordBotName
from utils.emojis import CROSS


def setup(bot: DiscordBotName):
    bot.logger.info(f"Loading Error Handling extension...")

    @bot.event
    async def on_application_command_error(inter: Interaction, error):
        if isinstance(error, ApplicationNotOwner):
            embed = Embed()
            embed.title = "**Missing Permissions**"
            embed.colour = Colour.red()
            embed.description = f"{CROSS} You must be the owner of the bot to use this command!"
            await inter.send(embed=embed)
        else:
            embed = Embed()
            embed.title = "**Application Command Error**"
            embed.colour = Colour.red()
            embed.description = f"{CROSS} {str(error)}"
            try:
                await inter.send(embed=embed)
            finally:
                raise error
