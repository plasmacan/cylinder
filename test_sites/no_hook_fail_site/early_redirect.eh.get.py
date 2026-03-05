def main(request, response, init, g, log, abort):
    # redirect to yahoo
    abort(307, "http://www.yahoo.com/")
