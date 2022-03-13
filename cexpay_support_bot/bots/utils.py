from pathlib import Path
from typing import Any
from chevron import render
import pkgutil

def render_message(package: str, template_name: str, data_context: Any) -> str:
	assert isinstance(package, str)
	assert isinstance(template_name, str)
	# assert isinstance(data_context, dict)

	templates_directory_path: Path = Path("templates")
	template_path: Path = templates_directory_path.joinpath(template_name)
	template_resource: str = template_path.as_posix()

	template_data_bytes = pkgutil.get_data(package, template_resource)
	if template_data_bytes is None:
		raise Exception("Not found template: %s" % template_name)

	template_data_str: str = template_data_bytes.decode("utf-8")

	render_result = render(template_data_str, data_context)

	assert isinstance(render_result, str)

	return render_result
