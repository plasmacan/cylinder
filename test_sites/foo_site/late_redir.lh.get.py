def main(request, response, init, g, abort):
    g.late_hook_run_count = getattr(g, "late_hook_run_count", 0) + 1
    abort(301, "/")
