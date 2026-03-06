import werkzeug

def main(request, response, init, g, log, abort):
    raise AbortCustom

class AbortCustom(werkzeug.exceptions.HTTPException):
    code = 599
    name = "Abort Custom"
    description = "My custom abort exception"