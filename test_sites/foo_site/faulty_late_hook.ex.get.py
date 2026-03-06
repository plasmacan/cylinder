def main(request, response, init, g, log):

    response.data = "this will fail because of an exception in late_hook"
    return response
