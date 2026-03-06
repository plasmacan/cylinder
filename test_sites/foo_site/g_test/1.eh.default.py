def main(request, response, init, g, log):
    g.early = "early hook executed"
    return response
