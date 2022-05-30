def main(flask, request, e, init, g, log):
    response = e.get_response()
    return str(response.data.decode("utf-8"))
