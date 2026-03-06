def main(request, response, init, g, log, abort):
    # redirect to google
    abort(307, "http://www.google.com/")
