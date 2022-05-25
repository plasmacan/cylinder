def main(flask, app, request, response, init, g, log):
    # redirect to google
    flask.abort(307, "http://www.google.com/")
