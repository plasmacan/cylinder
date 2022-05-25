def main(flask, app, request, response, init, g, log):
    response.data = "hello world"
    return response
