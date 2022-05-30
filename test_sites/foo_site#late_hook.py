def main(flask, request, response, init, g, log):
    response.headers["late_hook"] = "good"
    return response
