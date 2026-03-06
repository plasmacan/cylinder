def main(request, response, init, g, log):
    response.headers["late_hook"] = "alright"
    return response
