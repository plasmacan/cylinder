def main(e, response):
    # e.original_exception has the original exception
    # e.get_response() can give you the default response for this error
    response.data = str(e.original_exception)
    return response
