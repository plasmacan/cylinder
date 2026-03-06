def main(request, response, init, g, log, abort):
    # raise a 502 error which will be handled by our custom 502 handler
    abort(502)
