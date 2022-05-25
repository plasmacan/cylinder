import pathlib


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


def test_bad_case(foo_site_client):
    response = foo_site_client.get("/bad_case")
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


def test_txt(foo_site_client):
    response = foo_site_client.get("/static.txt")
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


def test_faulty_late_hook(foo_site_client):
    response = foo_site_client.get("/faulty_late_hook")
    assert "Late_hook" not in response.headers
    assert response.status_code == 500
    assert b"division by zero" in response.data


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


def test_not_implemented(foo_site_client):
    response = foo_site_client.delete("/")
    assert response.headers["Late_hook"] == "good"
    assert response.status_code == 501
    assert b"Not Implemented" in response.data


def test_error_returns_string(foo_site_client):
    response = foo_site_client.get("/error_returns_string")
    assert response.headers["Late_hook"] == "good"
    assert response.status_code == 418
    assert b"I am but a teapot, my friend" in response.data


def test_minimum_site(minimum_site_client):
    response = minimum_site_client.get("/test")
    assert response.status_code == 200
    assert b"hello world" in response.data


def test_no_hook_fail_site(no_hook_fail_site_client):
    response = no_hook_fail_site_client.get("/")
    assert response.status_code == 500
    assert b"there is an error in the application" in response.data


def test_logger(minimum_site_app, capsys):
    log = minimum_site_app.logger
    log.error("the logger works")
    captured = capsys.readouterr()
    assert "the logger works" in captured.err
