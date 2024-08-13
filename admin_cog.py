import discord
from discord import app_commands
from discord.ext import commands

from utils import *
from database_broker import Rivet2DatabaseBroker

def format_errcode_message(
		short_code: str | None,
		error_code: int,
		facility: str,
		subfacility: str | None,
		error_name: str | None,
		error_description: str | None,
		verbose: bool) -> str:
	# Wrap whole message in Markdown code block
	info_message = "```\n"

	critical = (error_code & CRITICAL_MASK)

	if verbose:
		info_message += f"Facility:    {facility}\n"

	if verbose and subfacility:
		info_message += f"Subfacility: {subfacility}\n"

	info_message += "\n"

	if short_code:
		info_message += f"{short_code} -> error code 0x{error_code:08X}"
	else:
		info_message += f"0x{error_code:08X}"

	if error_name:
		if critical: 
			info_message += f": 🚨{error_name}🚨\n"
		else:
			info_message += f": {error_name}\n"
	else:
		info_message += f": unknown {'CRITICAL' if critical else ''} error name (errnum=0x{error_code & ERROR_NUM_MASK:04X})\n"

	if error_description:
		info_message += "\n" + error_description + "\n"

	# Close code block
	info_message += "\n```"
	return info_message

class Rivet2AdminCog(commands.GroupCog, name="admin", description="Administration commands"):
	db_cmd_group = app_commands.Group(name="database", description="Database administration commands")

	def __init__(self, database: Rivet2DatabaseBroker):
		super().__init__()
		self.database = database

	@db_cmd_group.command(name="update", description="Update local databases from remote.")
	@commands.check(is_administrator)
	async def update_db(self, interaction: discord.Interaction) -> None:
		await interaction.response.send_message("<Database updates not implemented yet>")

	@db_cmd_group.command(name="reload", description="Reload local databases.")
	@commands.check(is_administrator)
	async def reload_db(self, interaction: discord.Interaction) -> None:
		self.database.reload_databases()
		await interaction.response.send_message("All databases reloaded.")