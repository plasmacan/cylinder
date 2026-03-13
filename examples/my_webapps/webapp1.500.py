import traceback


def main(response, e):
    tb_str = "".join(traceback.format_exception(e.original_exception))
    response.content_type = "text/plain; charset=UTF-8"
    response.data = tb_str
    return response
