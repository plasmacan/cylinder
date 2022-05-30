def main(flask, request, response, init, g, log):
    response.status = 200
    response.data = "PutteD!"
    return response
