def main(flask, request, response, init, g, log):
    request.data = "this will fail because of an exception in late_hook"
    return request.data
