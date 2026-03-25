import logging

import jinja2
import pytest

from src import cylinder
from test_sites import init as inittest
from types import SimpleNamespace

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("test_sites/templates"),
    auto_reload=True,
    autoescape=jinja2.select_autoescape(),
)


def render_template(template_name, **context):
    t = jinja_env.get_template(template_name)
    return t.render(context)


@pytest.fixture()
def foo_site_app():
    def app_map_func(request):

        return (
            "test_sites",
            "foo_site",
            {"init": inittest, "render_template": render_template, 'g': SimpleNamespace()},
        )

    app = cylinder.get_app(app_map_func, logging.DEBUG)
    app.wait_for_logs = True
    # other setup can go here

    return app

    # clean up / reset resources here


@pytest.fixture()
def no_hook_fail_site_app():
    def app_map_func(request):
        return (
            "test_sites",
            "no_hook_fail_site",
            {"init": inittest, "render_template": render_template},
        )

    app = cylinder.get_app(app_map_func, logging.DEBUG)
    app.wait_for_logs = True
    return app


@pytest.fixture()
def foo_site_client(foo_site_app):
    return foo_site_app.test_client()


@pytest.fixture()
def minimum_site_client(caplog):

    def app_map_func(request, g):
        return (
            "test_sites",
            "minimum_site",
            {"init": inittest, "render_template": render_template},
        )

    minimum_site_app = cylinder.get_app(app_map_func, logging.DEBUG)

    return minimum_site_app.test_client()


@pytest.fixture()
def no_hook_fail_site_client(
    no_hook_fail_site_app,
):
    return no_hook_fail_site_app.test_client()
