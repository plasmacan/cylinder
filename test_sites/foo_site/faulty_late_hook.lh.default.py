def main(request, response, init, g, log):
    # even if a late hook is broken, the 500 handler should still work
    1 / 0
    return response
