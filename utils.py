
import discord

# Error code bits information
IS_ERROR_MASK	= 0x80000000	#1 if error code; 0 otherwise
CRITICAL_MASK	= 0x40000000	#1 if critical error; 0 otherwise
RESERVED_MASK	= 0x30000000	#Always 0
FACILITY_MASK	= 0x0FFF0000	#Facility identifier
FACILITY_SHIFT	= 16
ERROR_NUM_MASK	= 0x0000FFFF	#Error number in facility
BITS_IN_ERROR_NUM = 16

SCE_ERROR_MASK	= (IS_ERROR_MASK | CRITICAL_MASK | RESERVED_MASK | FACILITY_MASK | ERROR_NUM_MASK)

def get_taihen_error_info(errcode: int) -> tuple[str | None, str | None]:
	TAIHEN_FACILIY_BASE = 0x90010000

	TAIHEN_ERRORS = [
		("TAI_ERROR_SYSTEM",				#0x90010000
   			"System error"),
		("TAI_ERROR_MEMORY",				#0x90010001
   			"Not enough memory available to complete operation"),
		("TAI_ERROR_NOT_FOUND",				#0x90010002
   			"Cannot find specified module or function"),
		("TAI_ERROR_INVALID_ARGS",			#0x90010003
			"Invalid arguments provided"),
		("TAI_ERROR_INVALID_KERNEL_ADDR",	#0x90010004
			"Invalid address (for KERNEL target process)"),
		("TAI_ERROR_PATCH_EXISTS",			#0x90010005
			"Hook or injection already exists at target address"),
		("TAI_ERROR_HOOK_ERROR",			#0x90010006
			"Error occurred in libsubstitute"),
		("TAI_ERROR_NOT_IMPLEMENTED",		#0x90010007
			"Hooking of SHARED module is not implemented"),
		("TAI_ERROR_USER_MEMORY",			#0x90010008
			"Invalid argument provided from userland\n(Did you forget to set the 'size' field?)"),
		("TAI_ERROR_NOT_ALLOWED",			#0x90010009
			"Caller doesn't have permissions to perform operation\n(Enable Unsafe Homebrew and build SELF as UNSAFE)"),
		("TAI_ERROR_STUB_NOT_RESOLVED",		#0x9001000A
			"Specified import has not been resolved yet, so it cannot be hooked"),
		("TAI_ERROR_INVALID_MODULE",		#0x9001000B
			"Invalid module ID provided"),
		("TAI_ERROR_MODULE_OVERFLOW",		#0x9001000C
			"Too many modules loaded in process"),
		("TAI_ERROR_BLOCKING"				#0x9001000D
			"Attempted to modify taiHEN configuration while in use"),
	]
	NUM_TAIHEN_ERRORS = len(TAIHEN_ERRORS)

	idx = (errcode - TAIHEN_FACILIY_BASE)

	if 0 <= idx <= NUM_TAIHEN_ERRORS:
		return TAIHEN_ERRORS[idx]

	return (None, None)

def could_be_PUID(value: int) -> bool:
	"""
	Returns True if the provided `value` might be a PUID.
	"""

	# PUID always have top nibble equal to 0x4
	if ((value & 0xF0000000) != 0x40000000):
		return False

	# UIDs are always odd
	if not (value & 1):
		return False

	# UIDs have non-zero value in bits <29:16>
	# More specifically, bits <19:16> should
	# always have at least one bit set.
	if ((value & 0xF0000) == 0):
		return False

	return True

# Callback for command checks
def is_administrator(interaction: discord.Interaction) -> bool:
    requester_id = interaction.user.id
    client = interaction.client

    if not hasattr(client, "rivet"):
        return False

    return (requester_id == client.rivet.bot.owner_id) or \
            requester_id in client.rivet.admin_whitelist
