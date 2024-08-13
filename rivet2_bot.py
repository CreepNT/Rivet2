# Python libraries
import logging
import tomllib
from typing import Type

# discord.py dependencies
import discord
from discord.ext import commands

# Rivet2 database
from database_broker import Rivet2DatabaseBroker

class Rivet2Bot():
    __slots__ = ["bot", "logger", "configuration", "admin_whitelist", "database"]

    def __init__(self, configuration_file):
        self.bot = commands.Bot(command_prefix=[], intents=discord.Intents.default())
        self.logger = logging.getLogger('discord.Rivet2')

        # Add a reference to the RivetBot on the discord.py Bot object
        self.bot.rivet = self

        with open(configuration_file, "rb") as cfg:
            self.configuration = tomllib.load(cfg)

        self.admin_whitelist = self.configuration["Bot"]["AdministratorWhitelist"]

        self.database = Rivet2DatabaseBroker(
            self.configuration["DatabaseFiles"]
        )


        @self.bot.event
        async def on_ready():
            self.logger.info(f"Bot logged in as '{self.bot.user}'")
            await self.bot.change_presence(
                activity=discord.CustomActivity("Resolving PSP2 error codes!", emoji="nerd"),
                status=discord.Status.online)
            self.logger.info(f"Changed presence successfully")

            await self.bot.tree.sync()
            self.logger.info(f"Synchronized slash commands successfully")

    def run(self):
        self.bot.run(token=self.configuration["Bot"]["DiscordToken"])
