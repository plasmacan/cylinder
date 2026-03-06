def main(request, response, init, g, log):

    response.data = "this will abort in late_hook"
    return response
