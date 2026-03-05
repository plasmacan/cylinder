import logging

import pytest

from src import cylinder


@pytest.fixture()
def foo_site_app():
    def dir_map_func(request):
        return "test_sites", "foo_site"

    app = cylinder.get_app(dir_map_func, logging.DEBUG)
    app.wait_for_logs = True
    # other setup can go here

    return app

    # clean up / reset resources here


@pytest.fixture()
def minimum_site_app():
    def dir_map_func(request):
        return "test_sites", "minimum_site"

    app = cylinder.get_app(dir_map_func, logging.DEBUG)
    app.wait_for_logs = True
    return app


@pytest.fixture()
def no_hook_fail_site_app():
    def dir_map_func(request):
        return "test_sites", "no_hook_fail_site"

    app = cylinder.get_app(dir_map_func, logging.DEBUG)
    app.wait_for_logs = True
    return app


@pytest.fixture()
def tiny_queue_app():
    def dir_map_func(request):
        return "test_sites", "minimum_site"

    app = cylinder.get_app(dir_map_func, logging.DEBUG, log_queue_length=1)
    app.wait_for_logs = True
    return app


@pytest.fixture()
def foo_site_client(foo_site_app):
    return foo_site_app.test_client()


@pytest.fixture()
def minimum_site_client(minimum_site_app):
    return minimum_site_app.test_client()


@pytest.fixture()
def no_hook_fail_site_client(
    no_hook_fail_site_app,
):
    return no_hook_fail_site_app.test_client()


@pytest.fixture()
def tiny_queue_client(tiny_queue_app):
    return tiny_queue_app.test_client()
