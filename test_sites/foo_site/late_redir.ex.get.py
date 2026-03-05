def main(request, response, init, g, log):

    response.data = "this will redirect in late_hook"
    return response
