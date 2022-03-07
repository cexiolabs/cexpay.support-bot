import json
from pathlib import Path
from chevron import render
import pkgutil

def read_json_templates(package: str, template_name: str) -> dict:
	assert isinstance(package, str)
	assert isinstance(template_name, str)

	templates_directory_path: Path = Path("")
	template_path: Path = templates_directory_path.joinpath(template_name)
	template_resource: str = template_path.as_posix()

	template_data_bytes = pkgutil.get_data(package, template_resource)
	if template_data_bytes is None:
		raise Exception("Not found template: %s" % template_name)

	template_data_str: str = template_data_bytes.decode("utf-8")

	json_data = json.loads(template_data_str)
	return json_data
