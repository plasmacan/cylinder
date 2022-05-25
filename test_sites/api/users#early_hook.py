def main(flask, app, request, response, init, g, log):
    # flask.abort(401)

    if request.path != "/" and request.url.endswith("/"):
        flask.abort(307, "/poop")

    response.headers["early_hook"] = "good"

    return response
