def main(request, response, init, g, log):
    response.data = "custom method blarg"
    return response
