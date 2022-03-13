import json
from pathlib import Path
from chevron import render
import pkgutil

def read_resource(resource_path: str) -> bytes:
	assert isinstance(resource_path, str)

	resource_data_bytes = pkgutil.get_data(__name__, resource_path)
	if resource_data_bytes is None:
		raise Exception("Not found template: %s" % resource_path)

	return resource_data_bytes

def read_resource_json(resource_path: str) -> dict:
	assert isinstance(resource_path, str)

	resource_data_bytes = read_resource(resource_path)

	resource_data_str: str = resource_data_bytes.decode("utf-8")

	json_data = json.loads(resource_data_str)

	return json_data
