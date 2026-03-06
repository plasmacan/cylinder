def main(request, response, init, g, log):
    response.data = str(g)
    return response
