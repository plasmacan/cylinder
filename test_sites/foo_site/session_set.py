def main(session, response):
    session["foo"] = "bar"
    return response
