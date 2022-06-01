def main(request, response, init, g, log, abort):
    # if you raise an exception that you don't have a handler for, flask will do it's best alone
    abort(401)
