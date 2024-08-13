import tomllib
from typing import Any

from utils import FACILITY_MASK, FACILITY_SHIFT, ERROR_NUM_MASK, BITS_IN_ERROR_NUM

# Database model classes
InformationRecord = dict[str, str]	# Allowed keys (per database schema): "name", "description"

def _cvt_db_to_runtime(database_map: dict[str, InformationRecord]) -> dict[int, InformationRecord]:
	"""
	Convert database map to runtime format
	"""
	rt_map = dict()
	for k, v in database_map.items():
		rt_key = int(k, 16)
		rt_map[rt_key] = v

	return rt_map

def _unpack_info_record(record: InformationRecord | None) -> tuple[str | None, str | None]:
	if not record:
		return (None, None)
	else:
		return (record.get("name"), record.get("description"))

class ErrorFacility():
	"""
	Error code facility class.

	This class represents an error code facility.
	"""
	def __init__(self, db_facility_object: dict):
		self._name = db_facility_object["name"]
		self._description = db_facility_object.get("description")

		# Allow facilities without 'error-codes' by falling back to empty dict.
		db_facilities = db_facility_object.get("error-codes", dict())
		self.error_codes = _cvt_db_to_runtime(db_facilities)

		# Allow facilities without 'invalid-ranges' by falling back to empty list.
		self.invalid_ranges = db_facility_object.get("invalid-ranges", [])

		# 'subfacility-bits' is only allowed if 'subfacilities' also exists
		sfbits = db_facility_object.get("subfacility-bits")
		if not sfbits:
			self.subfacilities = None
		else:
			self.subfacilities = _cvt_db_to_runtime(db_facility_object.get("subfacilities"))
			self.subfacility_format = f"0x%0{(sfbits + 3) // 4}X"
			self.subfacility_shift = BITS_IN_ERROR_NUM - sfbits
			self.subfacility_mask = ERROR_NUM_MASK >> self.subfacility_shift

	def name(self) -> str:
		return self._name

	def description(self) -> str | None:
		return self._description

	def is_invalid_error(self, error_code: int) -> bool:
		errnum = (error_code & ERROR_NUM_MASK)

		for inv_range in self.invalid_ranges:
			range_start = inv_range[0]
			range_end = inv_range[1]

			if range_start <= errnum <= range_end:
				return True
		return False			

	def get_error_information(self, error_code: int) -> tuple[str | None, str | None]:
		"""
		Returns (`error name`, `error description`) tuple.
		"""
		return _unpack_info_record(self.error_codes.get(error_code & ERROR_NUM_MASK))

	def has_subfacilities(self) -> bool:
		return (self.subfacilities != None)

	def get_error_subfacility_info(self, error_code: int) -> InformationRecord | None:
		if not self.subfacilities:
			return None
		
		sf_num = (error_code >> self.subfacility_shift) & self.subfacility_mask
		return self.subfacilities.get(sf_num)

class Rivet2DatabaseBroker():
	__slots__ = ["short_codes", "short_codes_db_path", "error_codes", "error_codes_db_path"]

	def _load_short_codes_database(self):
		with open(self.short_codes_db_path, "rb") as fd:
			self.short_codes = tomllib.load(fd)

	def _load_error_codes_database(self):
		with open(self.error_codes_db_path, "rb") as fd:
			database = tomllib.load(fd)

		for facility_num_str, facility_obj in database.items():
			facility_num = int(facility_num_str, 16)
			self.error_codes[facility_num] = ErrorFacility(facility_obj)

	def __init__(self, configuration: dict[str, Any]):
		self.short_codes: dict[str, int] = dict()
		self.error_codes: dict[int, ErrorFacility] = dict()

		self.short_codes_db_path = configuration["ShortCodeDatabase"]
		self.error_codes_db_path = configuration["ErrorDatabase"]

		self.reload_databases()

	def reload_databases(self):
		self._load_short_codes_database()
		self._load_error_codes_database()

	def get_error_for_short_code(self, short_error_code: str) -> int | None:
		return self.short_codes.get(short_error_code)
	
	def get_errcode_facility(self, error_code: int) -> ErrorFacility | None:
		facility_id = (error_code & FACILITY_MASK) >> FACILITY_SHIFT
		return self.error_codes.get(facility_id)
