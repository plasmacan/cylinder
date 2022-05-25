import logging

import pytest

from src import cylinder


@pytest.fixture()
def foo_site_app():
    def dir_map_func(request):  # pylint: disable=unused-argument
        return "test_sites", "foo_site"

    app = cylinder.get_app(dir_map_func, logging.DEBUG)
    # other setup can go here

    return app

    # clean up / reset resources here


@pytest.fixture()
def minimum_site_app():
    dir_map = ("test_sites", "minimum_site")
    app = cylinder.get_app(dir_map, logging.DEBUG)
    return app


@pytest.fixture()
def no_hook_fail_site_app():
    dir_map = ("test_sites", "no_hook_fail_site")
    app = cylinder.get_app(dir_map, logging.DEBUG)
    return app


@pytest.fixture()
def foo_site_client(foo_site_app):  # pylint: disable=redefined-outer-name
    return foo_site_app.test_client()


@pytest.fixture()
def minimum_site_client(minimum_site_app):  # pylint: disable=redefined-outer-name
    return minimum_site_app.test_client()


@pytest.fixture()
def no_hook_fail_site_client(
    no_hook_fail_site_app,
):  # pylint: disable=redefined-outer-name
    return no_hook_fail_site_app.test_client()
