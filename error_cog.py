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
		info_message += f": unknown{' CRITICAL ' if critical else ' '}error name (errnum=0x{error_code & ERROR_NUM_MASK:04X})\n"

	if error_description:
		info_message += "\n" + error_description + "\n"

	# Close code block
	info_message += "\n```"
	return info_message

class Rivet2ErrorCog(commands.Cog):
	def __init__(self, database: Rivet2DatabaseBroker):
		self.database = database

	@app_commands.command(
		name="ec",
		description="Get information about an SCE error code"
	)
	async def get_errcode_info(self, interaction: discord.Interaction, error: str, verbose: bool = True) -> None:
		"""
		Parameters
		----------
		error: str
			Error code (hex integer or SCE short error code)
		"""
		# None-initialize all variables we will need at the end,
		# but that may not be initialized by certain code pathes.
		short_code = None
		facilityIdentity = None
		subfacilityIdentity = None
		errorName = None
		errorDescription = None

		# Attempt to parse as hexadecimal integer
		try:
			errcode = int(error, 16)

			# Negative values are converted to 64-bit automatically.
			# Mask top 32 bits to obtain the error code we care about.
			if error[0] == '-':
				errcode &= 0xFFFFFFFF

		except ValueError:
			# Failed to parse: must be a short error code
			errcode = self.database.get_error_for_short_code(error)
			if not errcode:
				return await interaction.response.send_message(
					f"`{error}` is an invalid input or unknown short error code."
				)

			short_code = error

		if ((errcode & SCE_ERROR_MASK) != errcode):
			return await interaction.response.send_message(
				f"0x{errcode:X} is too long (SCE error codes are 32 bits)"
			)

		if not (errcode & IS_ERROR_MASK):
			# Not an error. Depending on called API, it could be a valid SceUID.
			# If basic heuristics say it could, add a little warning for the user.
			reply = f"0x{errcode:08X} is not a valid SCE error (error bit is clear)."
			if could_be_PUID(errcode):
				reply += "\nAre you sure this isn't a valid SceUID instead?"
			return await interaction.response.send_message(reply)

		if (errcode & RESERVED_MASK):
			# Check if this is a taiHEN error, which have a reserved bit set.
			(errorName, errorDescription) = get_taihen_error_info(errcode)
			if errorName:
				facilityIdentity = "taiHEN"
			else:
				return await interaction.response.send_message(
					f"0x{errcode:08X} is not a valid SCE error (reserved bit(s) not clear)."
				)

		# If not already found (i.e., not a taiHEN error), search for error code in database
		if not facilityIdentity:
			f = self.database.get_errcode_facility(errcode)
			if f:
				facilityIdentity = f.name()
				if f.description():
					facilityIdentity += f"\n({f.description()})"
				
				# Check if there are subfacilities - if so, try to find stuff about it.
				if f.has_subfacilities():
					sf = f.get_error_subfacility_info(errcode)
					if sf:
						subfacilityIdentity = sf["name"]
						if sf.get("description"):
							subfacilityIdentity += f"\n({sf['description']})"

				(errorName, errorDescription) = f.get_error_information(errcode)							

		# Could not find information about the error code in the database...
		if not facilityIdentity:
			reply = f"Could not find information about error code 0x{errcode:08X}"
			# But the value might be a pointer - print this as hint in response.
			if errcode >= 0x81000000:
				reply += " - are you sure this isn't a pointer?"
			else:
				reply += "."
			return await interaction.response.send_message(reply)

		# Found a facility, and maybe more... format the message how user wants and print it.
		return await interaction.response.send_message(
			format_errcode_message(short_code, errcode, facilityIdentity, subfacilityIdentity,
						  			errorName, errorDescription, verbose)
		)
