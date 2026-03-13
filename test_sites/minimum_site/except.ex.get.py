def main(response):
    response.data = 1/0
    return response
