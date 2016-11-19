import unicodedata

def remove_accents(input_str):
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def validate_app_id(app_id):
	return True

def app_id_from_name(app_name):
	app_id = "_".join(s for s in remove_accents(app_name.strip()).lower().split() if s)
	return app_id if validate_app_id(app_id) else None

def get_dashed_app_id(app_id):
	return app_id.replace("_", "-")

def get_app_dir_name(app_id):
	return "nuvola-app-" + get_dashed_app_id(app_id)
