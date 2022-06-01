def main(response):
    response.data = "this 502 was changed to 200"
    response.status_code = 200
    return response
