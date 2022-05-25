def main(flask, app, request, response, init, g, log):
    # even if a late hook is broken, the 500 handler should still work
    return 1 / 0
