import json

with open("./db.json", "rb") as fd:
	db = json.load(fd)

with open("./conv.toml", "w") as out:
	for fnum, fcontent in db.items():
		facility_name = fcontent['name']
		facility_description = fcontent.get('description')
		blacklist = fcontent.get('blacklist')
		errors = fcontent.get('errors')
		
		print(f'[{fnum}]', file=out)
		print(f'\tname = "{facility_name}"', file=out)

		if facility_description:
			print(f'\tdescription = "{facility_description}"\n', file=out)

		if blacklist:
			print(f'\tinvalid-ranges = [', file=out)
			for banned_range in blacklist:
				print(f'\t\t[{banned_range['min']}, {banned_range['max']}],', file=out)
			print(f'\t]\n', file=out)

		if errors:
			print(f'\t[{fnum}.error-codes]', file=out)
			for errnum, errcontent in errors.items():
				errname = errcontent.get('name')
				errdesc = errcontent.get('description')
				
				print(f'\t\t{errnum} = {"{"}', end="", file=out)
				if errname:
					print(f' name = "{errname}"', end="", file=out)
				if errdesc:
					if errname:
						print(',', end="", file=out)
					print(f' description = "{errdesc.replace("\n", "\\n")}"', end="", file=out)
				print(" }", file=out)

		print("", file=out)

print("done")