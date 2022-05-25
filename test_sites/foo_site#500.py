def main(flask, app, request, e, init, g, log):
    # e.original_exception has the original exception
    # e.get_response() can give you the default response for this error
    response = e.get_response()
    response.data = str(e.original_exception)
    return response
