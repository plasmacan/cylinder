import json


def main(request, response, init, g, log, abort):
    # an early hook can be used to handle things like removing trailing slashes
    if request.base_url.endswith("/") and request.path != "/":
        new_base_url = request.base_url.rstrip("/")
        if request.query_string:
            abort(308, f"{new_base_url}?{request.query_string.decode('utf-8')}")
        else:
            abort(308, new_base_url)

    # also for setting things on a response
    response.access_control_allow_origin = "*"
    response.access_control_allow_methods = "*"
    response.headers["early_hook"] = "good"

    # or to perform request validation
    if request.is_json:  # mimetype is application/json
        try:
            json.loads(request.data)
        except Exception:
            abort(400, "invalid json provided")

    return response
