# Rivet2

Helper Discord bot for SCE PSP2 error codes.

# Installation

1. `pip install -r requirements.txt`
2. `mv rivet2_config_template.toml rivet2_config.toml`
3. Fill `rivet2_config.toml` as desired
4. `python3 main.py`

# Database format

```toml
# At top-level, the database file contains facilities.

[0x000]	# Facility header - must be the facility's number IN HEXADECIMAL
	name = "Facility name"				# Mandatory: facility name
	description = "Facility description"		# Optional: facility description

	# Optional: invalid error number ranges
	invalid-ranges = [
		[0x0010, 0x001F],	# This marks all error numbers between [0] and [1],
		[0x0030, 0x003F],	# both bounds included, as not valid for this facility.
		[0x0050, 0xFFFF]	# <--- EXAMPLE: this marks [0x0050, 0xFFFF] as invalid.
	]

	# Optional: subfacilities information
	[0x000.subfacilities]
		# Number of bits at top of error number holding subfacility ID
		# Mandatory if the [subfacilities] section is present
		bits-for-subfacility = 8

		# This section contains one entry for each subfacility.
		# Key is subfacility ID (IN HEXADECIMAL), value is inline table containing:
		0x00 = { name = "SF0" }				# 'name': subfacility name (mandatory)
		0x01 = { name = "SF1", description = "Sub1" }	# 'description': subfacility description (optional)

	# Optional: facility error codes information
	[0x000.error-codes]
		# This section contains one entry for each error code.
		# Key is error code number (IN HEXADECIMAL), value is inline table
		# containing the same fields 'name' and 'description' as subfacilities.
		# By convention, error codes are sorted in ascending order, and each
		# subfacility is prefixed with a comment, as follows:

		# Subfacility 0 errors
		0x0000 = { name = "F0_SF0_ERR0", description = "SF0 Error 0" }
		0x0001 = { name = "F0_SF0_ERR1" }

		# Subfacility 1 errors
		0x0100 = { description = "SF1 Error 0" }
```

The `scripts/convert_old_to_new.py` script can be used to migrate from the old Rivet database format to the Rivet2 database format.