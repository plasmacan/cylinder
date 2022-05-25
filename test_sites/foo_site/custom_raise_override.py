def main(flask, app, request, response, init, g, log):
    # raise a 502 error which will be handled by our custom 502 handler
    flask.abort(502)
