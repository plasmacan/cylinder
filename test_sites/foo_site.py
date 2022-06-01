def main(request, response, init, g, log, render_template, abort):
    # this is the main entry point for the root of the website.
    # unless there is a more specific file to match the path of the URL, then all requests will land here.
    # it is therefore necessessery to manually implement 404 here, otherwise there is no 404.

    if request.path == "/":
        response.data = render_template("hello.html", name="Chris")
        return response
    else:
        abort(404)
