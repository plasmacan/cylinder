import json


def main(flask, app, request, response, init, g, log):
    # an early hook can be used to handle things like removing trailing slashes
    if request.base_url.endswith("/") and request.path != "/":
        new_base_url = request.base_url.rstrip("/")
        if request.query_string:
            flask.abort(308, f"{new_base_url}?{request.query_string.decode('utf-8')}")
        else:
            flask.abort(308, new_base_url)

    # also for setting things on a response
    response.access_control_allow_origin = "*"
    response.access_control_allow_methods = "*"
    response.headers["early_hook"] = "good"

    # or to perform request validation
    if request.is_json:  # mimetype is application/json
        try:
            json.loads(request.data)
        except Exception:
            flask.abort(400, "invalid json provided")

    return response
