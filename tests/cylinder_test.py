import logging
import pathlib
import sys
import time

from src import cylinder
from test_sites import init as inittest


def test_root_tripple(foo_site_client):
    # run twice so that the init_modules cache is non-empty at least once
    # also touch the template so that the template cache must update
    response = foo_site_client.get("/")
    assert b"hello, Chris" in response.data
    assert response.headers["Early_hook"] == "good"
    assert response.headers["Late_hook"] == "good"
    assert response.status_code == 200

    response = foo_site_client.get("/")
    assert b"hello, Chris" in response.data
    assert response.headers["Early_hook"] == "good"
    assert response.headers["Late_hook"] == "good"
    assert response.status_code == 200

    pathlib.Path("test_sites/templates/hello.html").touch()

    response = foo_site_client.get("/")
    assert b"hello, Chris" in response.data
    assert response.headers["Early_hook"] == "good"
    assert response.headers["Late_hook"] == "good"
    assert response.status_code == 200


def test_g(foo_site_client):
    # confirms g can be reused from hook to hook within a single request
    # confirms that g doesn't leak data between requests
    response = foo_site_client.get("g_test/1")
    assert b"early hook executed" in response.data
    assert b"1 executed" in response.data
    response = foo_site_client.get("g_test/2")
    assert b"2 executed" in response.data
    assert b"early hook executed" not in response.data
    assert b"1 executed" not in response.data


def test_reserved_method(foo_site_client):
    response = foo_site_client.open("/", method="DEFAULT")
    assert response.status_code == 500
    assert b"is reserved" in response.data


def test_bad_method_case(foo_site_client):
    response = foo_site_client.open("/", method="f12")
    assert response.status_code == 500
    print(response.data)
    assert b"only alpha" in response.data


def test_bad_case(foo_site_client):
    response = foo_site_client.get("/bad_case")
    assert response.status_code == 404


def test_bad_case_direct(foo_site_client):
    response = foo_site_client.get("/bad_case.Get.py")
    assert response.status_code == 404


def test_exception(foo_site_client):
    response = foo_site_client.get("/an_exception")
    assert response.headers["Late_hook"] == "good"
    assert response.status_code == 500
    assert b"division by zero" in response.data


def test_redirect(foo_site_client):
    response = foo_site_client.get("/a_redirect")
    assert response.headers["Late_hook"] == "good"
    assert response.headers["Location"] == "http://www.google.com/"
    assert response.status_code == 307


def test_csv(foo_site_client):
    response = foo_site_client.get("/static.csv")
    assert response.headers["Early_hook"] == "good"
    assert response.headers["Late_hook"] == "good"
    assert response.headers["Content-Type"] in [
        "application/vnd.ms-excel",
        "text/csv; charset=utf-8",
    ]
    assert b"static csv" in response.data
    assert response.status_code == 200


def test_req_id(caplog):
    def app_map_func(request, g):
        return "test_sites", "foo_site", {"init": inittest}

    foo_site_app = cylinder.get_app(app_map_func, log_handler=caplog.handler)
    foo_site_client = foo_site_app.test_client()
    response = foo_site_client.get("/", headers={"X-Request-ID": "custom_req"})
    assert foo_site_app.global_proxy.request_id == "custom_req"

    foo_site_app = cylinder.get_app(
        app_map_func, log_handler=caplog.handler, request_id_header=None
    )
    foo_site_client = foo_site_app.test_client()
    response = foo_site_client.get("/")
    assert foo_site_app.global_proxy.request_id.startswith("req_")

    foo_site_app = cylinder.get_app(
        app_map_func, log_handler=caplog.handler, request_id_header="CF-Ray"
    )
    foo_site_client = foo_site_app.test_client()
    response = foo_site_client.get("/", headers={"CF-Ray": "custom_req2"})
    assert foo_site_app.global_proxy.request_id == "custom_req2"


def test_txt(foo_site_client):
    response = foo_site_client.get("/static.txt")
    assert response.headers["Early_hook"] == "good"
    assert response.headers["Late_hook"] == "good"
    assert response.headers["Content-Type"] == "text/plain; charset=utf-8"
    assert b"static txt" in response.data
    assert response.status_code == 200


def test_path_traversal(foo_site_client):
    response = foo_site_client.get("/../../static.txt")
    assert response.headers["Early_hook"] == "good"
    assert response.headers["Late_hook"] == "good"
    assert response.headers["Content-Type"] == "text/plain; charset=utf-8"
    assert b"static txt" in response.data
    assert response.status_code == 200


def test_txt_gz(foo_site_client):
    response = foo_site_client.get("/static.txt.gz")
    assert response.headers["Early_hook"] == "good"
    assert response.headers["Late_hook"] == "good"
    assert response.headers["Content-Type"] == "text/plain; charset=utf-8"
    assert response.headers["Content-Encoding"] == "gzip"
    assert b"static.txt" in response.data
    assert response.status_code == 200


def test_early_hook_returns_string(foo_site_client):
    response = foo_site_client.delete("/early_delete")
    assert response.status_code == 500
    assert b"return the same response passed in" in response.data


def test_late_hook_returns_string(foo_site_client):
    response = foo_site_client.put("/faulty_late_hook")
    assert response.status_code == 500
    assert b"return the same response passed in" in response.data


def test_custom_raise(foo_site_client):
    response = foo_site_client.get("/custom_raise")
    assert response.status_code == 599
    assert b"My custom abort exception" in response.data


def test_custom_raise_override(foo_site_client):
    response = foo_site_client.get("/custom_raise_override")
    assert response.headers["Late_hook"] == "good"
    assert response.status_code == 200
    assert b"502 was changed to 200" in response.data


def test_custom_raise_default(foo_site_client):
    response = foo_site_client.get("/raise_default")
    assert response.headers["Late_hook"] == "good"
    assert b"Unauthorized" in response.data
    assert response.status_code == 401


def test_trailing_slash(foo_site_client):
    response = foo_site_client.get("/test/")
    assert response.status_code == 308
    assert response.headers["Late_hook"] == "good"
    assert response.headers["Location"].endswith("/test")


def test_404(foo_site_client):
    response = foo_site_client.get("/test")
    assert response.status_code == 404
    assert response.headers["Late_hook"] == "good"


def test_put(foo_site_client):
    response = foo_site_client.put("/test", data="{}")
    assert response.headers["Late_hook"] == "good"
    assert response.headers["Early_hook"] == "good"
    assert b"PutteD!" in response.data
    assert response.status_code == 200


def test_broken_put(foo_site_client):
    response = foo_site_client.put(
        "/test", data="{", headers={"Content-Type": "application/json"}
    )
    assert response.headers["Late_hook"] == "good"
    assert b"Bad Request" in response.data
    assert b"invalid json provided" in response.data
    assert response.status_code == 400


def test_broken_template(foo_site_client):
    response = foo_site_client.get("/bad_template")
    assert response.headers["Late_hook"] == "good"
    assert response.status_code == 500
    assert b"9usdhf9ubsd.html" in response.data


def test_early_abort(foo_site_client):
    response = foo_site_client.post("/early_post")
    assert response.status_code == 405


def test_bad_syntax(foo_site_client):
    response = foo_site_client.get("/bad_syntax")
    assert response.status_code == 500
    assert b"invalid syntax" in response.data


def test_py_bypass(foo_site_client):
    response = foo_site_client.get("/faulty_late_hook.py")
    assert response.status_code == 404


def test_case_bypass(foo_site_client):
    response = foo_site_client.get("/faulty_late_hook.PY")
    assert response.status_code == 404


def test_not_implemented(foo_site_client):
    response = foo_site_client.delete("/")
    assert response.headers["Late_hook"] == "good"
    assert response.status_code == 501
    assert b"Not Implemented" in response.data


def test_return_string(foo_site_client):
    response = foo_site_client.get("/return_string")
    assert response.headers["Late_hook"] == "good"
    assert response.status_code == 500
    assert b"return the same response passed in" in response.data


def test_error_returns_string(foo_site_client):
    response = foo_site_client.get("/error_returns_string")
    assert response.headers["Late_hook"] == "good"
    assert response.status_code == 500
    assert b"return the same response passed in" in response.data


def test_no_method_bypass(foo_site_client):
    response = foo_site_client.open("/", method="early")
    assert response.status_code == 501
    assert "Early_hook" not in response.headers


def test_custom_method(foo_site_client):
    response = foo_site_client.open("/custom_method", method="BLARG")
    assert response.status_code == 200
    assert b"blarg" in response.data
    assert response.headers["Early_hook"] == "good"
    assert response.headers["Late_hook"] == "alright"


def test_minimum_site(minimum_site_client):
    response = minimum_site_client.get("/test")
    assert response.status_code == 200
    assert b"hello world" in response.data

def test_minimum_site_exception(caplog):
    def app_map_func(request, g):
        return "test_sites", "minimum_site", {"init": inittest}

    minimum_site_app = cylinder.get_app(app_map_func, log_handler=caplog.handler)
    minimum_site_client = minimum_site_app.test_client()

    response = minimum_site_client.get("/except")
    minimum_site_app.log_queue.join()

    assert response.status_code == 500
    assert 'division by zero' in caplog.text


def test_minimum_site_exception_in_exception_handler(caplog):
    def app_map_func(request, g):
        return "test_sites", "minimum_site", {"init": inittest}

    minimum_site_app = cylinder.get_app(app_map_func, log_handler=caplog.handler)
    minimum_site_client = minimum_site_app.test_client()

    response = minimum_site_client.get("/except2")
    minimum_site_app.log_queue.join()

    assert response.status_code == 500
    assert 'division by zero' in caplog.text


def test_no_hook_fail_site(no_hook_fail_site_client):
    response = no_hook_fail_site_client.get("/")
    assert response.status_code == 500
    assert b"there is an error in the application" in response.data


def test_request_wait(capsys):

    def app_map_func(request, g):
        return "test_sites", "minimum_site", {}

    minimum_site_app = cylinder.get_app(app_map_func, logging.DEBUG)

    minimum_site_app.wait_for_logs = True
    test_client = minimum_site_app.test_client()
    test_client.get("/test")
    test_client.get("/test")

    captured1 = capsys.readouterr()

    # wait for the logger queue to drain
    while not minimum_site_app.log_queue.empty():
        time.sleep(0.01)

    captured2 = capsys.readouterr()

    assert len(captured1.err) > 0
    assert len(captured2.err) == 0


def test_request_nowait(capsys):

    def app_map_func(request, g):
        return "test_sites", "minimum_site", {}

    minimum_site_app = cylinder.get_app(app_map_func, logging.DEBUG)

    minimum_site_app.wait_for_logs = False
    test_client = minimum_site_app.test_client()
    test_client.get("/test")
    test_client.get("/test")

    captured1 = capsys.readouterr()
    sys.stderr.write(captured1.err)

    # wait for the logger queue to drain
    while not minimum_site_app.log_queue.empty():
        time.sleep(0.01)

    captured2 = capsys.readouterr()

    assert len(captured1.err) < len(captured2.err)


def test_invalid_app_map(capsys):
    try:
        tiny_queue_app = cylinder.get_app("app_map", logging.DEBUG, log_queue_length=1)
        assert False, "there should be a ValueError exception"
    except ValueError as e:
        assert "app_map must be a function" in str(e)


def test_logger_full(capsys):

    def app_map_func(request, g):
        return "test_sites", "minimum_site", {}

    tiny_queue_app = cylinder.get_app(app_map_func, logging.DEBUG, log_queue_length=1)

    # the buffer only holds 1, this test fills is up
    log = tiny_queue_app.logger
    for num in range(10):
        log.error(f"test_logger_full {num}")

    # wait for the logger to finish output
    while not tiny_queue_app.log_queue.empty():
        time.sleep(0.01)

    captured = capsys.readouterr()
    assert (
        len(captured.err.splitlines()) < 10
    )  # lines had to be dropped if buffer was full
    assert len(captured.err.splitlines()) > 0


def test_faulty_late_hook(caplog):
    def app_map_func(request, g):
        return "test_sites", "foo_site", {"init": inittest}

    foo_site_app = cylinder.get_app(app_map_func, log_handler=caplog.handler)
    foo_site_client = foo_site_app.test_client()

    response = foo_site_client.get("/faulty_late_hook")

    assert "Late_hook" not in response.headers
    assert response.status_code == 500
    assert b"division by zero" in response.data

    foo_site_app.log_queue.join()

    print(f"{caplog.text=} {foo_site_app.log_queue=}")


def test_late_redirect(foo_site_client, no_hook_fail_site_client):
    response = foo_site_client.get("/late_redir")
    assert not response.headers.get("Late_hook")
    assert response.status_code == 301
    assert response.headers["Location"] == "/"

    response = no_hook_fail_site_client.get("/a_redirect")
    assert response.status_code == 307
    assert response.headers["Location"] == "http://www.google.com/"


def test_late_redirect_no_late_hook(no_hook_fail_site_client):
    response = no_hook_fail_site_client.get("/early_redirect")
    assert response.status_code == 307
    assert response.headers["Location"] == "http://www.yahoo.com/"


def test_late_abort():

    def app_map_func(request, g):
        return "test_sites", "foo_site", {"init": inittest}

    foo_site_app = cylinder.get_app(app_map_func)
    foo_site_client = foo_site_app.test_client()

    response = foo_site_client.get("/late_abort")
    foo_site_app.log_queue.join()

    assert response.status_code == 401
    assert b"not today" in response.data
    assert foo_site_app.global_proxy.g.late_hook_run_count == 1, (
        "late hook should only run once"
    )
