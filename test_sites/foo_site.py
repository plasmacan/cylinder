def main(flask, request, response, init, g, log):
    # this is the main entry point for the root of the website.
    # unless there is a more specific file to match the path of the URL, then all requests will land here.
    # it is therefore necessessery to manually implement 404 here, otherwise there is no 404.

    if request.path == "/":
        response.data = flask.render_template("hello.html", name="Chris")
        return response
    else:
        flask.abort(404)
