#!/bin/env python3

# Import bot core and all cogs
from rivet2_bot import Rivet2Bot
from error_cog import Rivet2ErrorCog
from admin_cog import Rivet2AdminCog

# Initialize bot core
rivet = Rivet2Bot("rivet2_config.toml")

# Instanciate cogs
error_cog = Rivet2ErrorCog(rivet.database)
admin_cog = Rivet2AdminCog(rivet.database)

# Install hook to add all cogs to bot
async def add_all_cogs():
        await rivet.bot.add_cog(error_cog)
        await rivet.bot.add_cog(admin_cog)

rivet.bot.setup_hook = add_all_cogs

# Start the bot
rivet.run()