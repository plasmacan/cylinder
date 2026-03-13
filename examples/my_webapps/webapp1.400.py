import traceback
import json


def main(request, response, e, log):
    tb_str = "".join(traceback.format_exception(e))
    log.error("Got a 400 error: %s", tb_str)
    response.content_type = "application/json; charset=UTF-8"
    response.data = json.dumps({"message": "bad_request", "status": 400, "error": True})
    return response
