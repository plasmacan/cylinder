def main(request, response, init, g, log, e):
    response.data=str(e)
    return response