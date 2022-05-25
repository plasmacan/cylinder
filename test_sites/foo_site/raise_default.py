def main(flask, app, request, response, init, g, log):
    # if you raise an exception that you don't have a handler for, flask will do it's best alone
    flask.abort(401)
