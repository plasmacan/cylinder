def main(request, response, init, g, log):
    response.headers["late_hook"] = "good"
    assert request.shallow == False
    return response
