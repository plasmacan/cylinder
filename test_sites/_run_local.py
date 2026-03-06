import os
import sys
import waitress
import init
import jinja2
from pathlib import Path
import logging

this_file_path = Path(__file__).resolve()
this_file_directory  = this_file_path.parent
sys.path.insert(0, str(this_file_directory.parent))
import src.cylinder as cylinder

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(f"{this_file_directory / 'templates'}"),
    auto_reload=True,
    autoescape=jinja2.select_autoescape()
)

def render_template(template_name, **context):
    t = jinja_env.get_template(template_name)
    return t.render(context)

def main():
    app = cylinder.get_app(app_map, log_level=logging.DEBUG)
    waitress.serve(app, host="127.0.0.42", port=80)

def app_map(request, g):
    return this_file_directory, "foo_site", {'init':init, 'render_template':render_template}


if __name__ == "__main__":
    main()
