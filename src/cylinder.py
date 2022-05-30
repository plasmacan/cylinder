import copy
import importlib.util
import logging
import logging.handlers
import mimetypes
import os
import pathlib
import queue
import time
from datetime import datetime

import flask
import jinja2
import werkzeug

__version__ = "v0.0.3"


def get_app(dir_map, log_level=logging.INFO, log_queue_length=1000):
    app = flask.Flask(__name__, static_folder=None, template_folder=None)
    app.wait_for_logs = False
    app.url_map.add(werkzeug.routing.Rule("/", defaults={"path": "/"}, endpoint="index"))
    app.url_map.add(werkzeug.routing.Rule("/<path:path>", endpoint="catchall"))

    log_formatter = logFormatter(
        "%(levelname)s [%(asctime)s] %(filename)s:%(lineno)s %(request_id)s\n    %(message)s\n",
        "%Y-%m-%d %H:%M:%S.uuu%z",
    )

    log_handler = flask.logging.default_handler
    log_handler.setFormatter(log_formatter)
    app.log_queue = EvictQueue(log_queue_length)
    queue_listener = logging.handlers.QueueListener(app.log_queue, log_handler, respect_handler_level=True)
    root_logger = logging.getLogger()
    root_logger.handlers = [customQueueHandler(app.log_queue)]
    root_logger.setLevel(log_level)
    queue_listener.start()

    jinja_loader = jinja2.FunctionLoader(jinja_loader_function)
    app.jinja_options = {"auto_reload": True, "loader": jinja_loader}

    flask.abort = werkzeug.exceptions.Aborter(
        extra={
            301: redirectMovedPermanently,
            302: redirectFound,
            303: redirectSeeOther,
            307: redirectTemporaryRedirect,
            308: redirectPermanentRedirect,
        }
    )

    setup_before_request(app, dir_map)
    setup_catch_all(app)
    setup_after_request(app)
    setup_error_handler(app)
    return app


def setup_before_request(app, dir_map):
    init_modules = {}

    @app.before_request
    def before_request():
        if callable(dir_map):
            site_dir, site_name = dir_map(flask.request)
        else:
            site_dir, site_name = dir_map
        site_path = pathlib.Path.cwd() / site_dir
        site_root = site_path / site_name
        site_path_str = str(site_path)
        if site_path_str not in init_modules:
            init_modules[site_path_str] = get_module(str(site_path / "init.py"))
        flask.g._init = init_modules[site_path_str]
        flask.g._search_paths = get_search_paths(site_root, flask.request.path)
        flask.g._site_path = site_path
        flask.g._request_time = time.time()
        # _request_id required for logger (used in logger subclass)
        flask.g._request_id = f"req_{format(int(flask.g._request_time*1000), 'X')}"
        app.logger.debug(
            f"INCOMING_REQUEST: "
            f"{flask.request.remote_addr} "
            f"{flask.request.method} "
            f"{flask.request.url} "
            f"{flask.request.environ.get('SERVER_PROTOCOL', '')}"
        )
        flask.g._module_chain = get_processors(flask.request.method)  # can log messages, must come after _request_id
        _, processor, _ = flask.g._module_chain
        if not processor:
            flask.abort(501)


def setup_catch_all(app):
    @app.endpoint("index")
    @app.endpoint("catchall")
    def catch_all(path):  # pylint: disable=unused-argument
        response = flask.Response()

        for module in flask.g._module_chain:
            if module:
                app.logger.debug(f"passing request to {module.__name__}")
                start_time = time.time()
                response = run_func_with_dict(
                    {
                        "flask": flask,
                        "app": app,
                        "request": flask.request,
                        "response": response,
                        "init": flask.g._init,
                        "g": flask.g,
                        "log": app.logger,
                    },
                    module.main,
                )
                ms = round((time.time() - start_time) * 1000)
                app.logger.debug(f"{module.__name__} completed in {ms}ms")

        return response


def setup_after_request(app):
    @app.after_request
    def after_request(response):
        ms = round((time.time() - flask.g._request_time) * 1000)
        app.logger.info(
            f"{flask.request.remote_addr} "
            f"{flask.request.method} "
            f"{flask.request.url} "
            f"{flask.request.environ.get('SERVER_PROTOCOL', '')} | {response.status}"
        )
        app.logger.debug(f"REQUEST_COMPLETE in {ms}ms.")

        if app.wait_for_logs:
            while not app.log_queue.empty():
                time.sleep(0.01)

        return response


def setup_error_handler(app):
    @app.errorhandler(redirectCustomClass)
    def http_redirect(e):
        app.logger.debug(f"abort redirect {e.code} raised.")
        response = flask.make_response("", e.code, {"Location": e.description})
        return late_hook_hail_mary(app, response)

    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def http_exception(e):
        app.logger.debug(f"abort code {e.code} raised.")
        custom_handler = get_http_error_handler(e.code)
        if not custom_handler:
            app.logger.debug(f"no custom handler registered for error {e.code}")
            response = e.get_response()
        else:
            app.logger.debug(f"using error handler: {custom_handler.__name__}")
            start_time = time.time()
            response = run_func_with_dict(
                {
                    "flask": flask,
                    "app": app,
                    "request": flask.request,
                    "e": e,
                    "response": e.get_response(),
                    "init": flask.g._init,
                    "g": flask.g,
                    "log": app.logger,
                },
                custom_handler.main,
            )
            ms = round((time.time() - start_time) * 1000)
            app.logger.debug(f"{custom_handler.__name__} completed in {ms}ms")

            # normalize the response variable into an actual flask response object
            if isinstance(response, (str, dict, bytes)):
                response = flask.make_response(response, e.code)
            if isinstance(response, tuple):
                response = flask.make_response(response)

        return late_hook_hail_mary(app, response)


def late_hook_hail_mary(app, response):
    # late_hook_hail_mary() will attempt to pass a copy of the response through a late_hook.
    # if the late_hook throws an exception, then then the copy is discarded and the original response is returned.
    # if late_hook succeeds, then the modified copy of the response is returned.
    _, _, late_hook = flask.g._module_chain
    if late_hook:
        try:
            app.logger.debug(f"passing request to {late_hook.__name__}")
            start_time = time.time()
            # by making a copy first, we can be sure late_hook cannot alter the
            # response unless it does not except
            copy.deepcopy(response)
            response = run_func_with_dict(
                {
                    "flask": flask,
                    "app": app,
                    "request": flask.request,
                    "response": response,
                    "init": flask.g._init,
                    "g": flask.g,
                    "log": app.logger,
                },
                late_hook.main,
            )
            ms = round((time.time() - start_time) * 1000)
            app.logger.debug(f"{late_hook.__name__} completed in {ms}ms")
        except Exception as x:
            app.logger.error(
                f'Got exception "{x}" at line {x.__traceback__.tb_next.tb_lineno} '  # pylint: disable=no-member
                f"in {late_hook.__name__}, continuing anyway"
            )
    return response


def jinja_uptodate_closure(template):

    last_mtime = os.path.getmtime(template)

    def up_to_date():
        if os.path.exists(template) and last_mtime == os.path.getmtime(template):
            return True
        return False

    return up_to_date


def jinja_loader_function(name):
    template = flask.g._site_path / "templates" / name
    if os.path.exists(template):
        with open(template, "r", encoding="UTF-8") as f:
            template_content = f.read()
        uptodate_func = jinja_uptodate_closure(template)
        return (template_content, name, uptodate_func)
    return None


def get_module(path):
    if not path:
        return None
    spec = importlib.util.spec_from_file_location(path, path)
    dynamic_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dynamic_module)
    return dynamic_module


def get_http_error_handler(error_code):
    file_path = find_processor_path([error_code])
    return get_module(file_path)


def get_processors(http_method):

    early_hook_file = find_processor_path([f"early_hook.{http_method}", "early_hook"])
    early_hook = get_module(early_hook_file)

    if http_method == "GET":
        direct_path = flask.g._search_paths[-1]
        if os.path.isfile(direct_path) and not str(direct_path).endswith(".py"):
            processor = directFileServe
        else:
            processor_file = find_processor_path(["GET", ""])
            processor = get_module(processor_file)
    else:
        processor_file = find_processor_path([f"{http_method}"])
        processor = get_module(processor_file)

    late_hook_file = find_processor_path([f"late_hook.{http_method}", "late_hook"])
    late_hook = get_module(late_hook_file)

    return (early_hook, processor, late_hook)


def find_processor_path(suffix_list):
    for path in reversed(flask.g._search_paths):
        for suffix in suffix_list:
            if suffix:
                potential_file = f"{path}#{suffix}.py"
            else:
                potential_file = f"{path}.py"
            # pathlib .resolve() is here to handle the case-insensitivity of windows. Enforces case to match
            if os.path.isfile(potential_file) and str(pathlib.Path(potential_file).resolve()) == potential_file:
                return potential_file
    return None


def get_search_paths(site_path, url_path_str):
    part_list = url_path_str.strip("/").split("/")
    results = [site_path]
    for part in part_list:
        if part and part != "..":  # path traversal protection
            results.append(results[-1] / part)
    return results


def run_func_with_dict(input_dict, func):
    arg_count = func.__code__.co_argcount
    var_names = func.__code__.co_varnames
    params = var_names[:arg_count]
    input_list = []
    for param in params:
        input_list.append(input_dict[param])
    return func(*input_list)


class directFileServe:
    def main(response, g):
        # pylint: disable=no-self-argument
        # no-member?
        direct_path = g._search_paths[-1]
        mimetype, content_encoding = mimetypes.guess_type(direct_path, strict=False)

        if content_encoding:
            response.content_encoding = content_encoding

        response.mimetype = mimetype or "application/octet-stream"

        with open(direct_path, "rb") as f:
            response.data = f.read()
        return response


class customQueueHandler(logging.handlers.QueueHandler):
    """Extend QueueHandler to attach Flask request context to record since
    request context won't be available inside listener thread.
    """

    def prepare(self, record):
        try:
            record.request_id = flask.g._request_id
        except Exception:
            record.request_id = ""
        return record


class logFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        formatted_time = time.strftime(datefmt, self.converter(record.created))
        formatted_time = formatted_time.replace("uuu", datetime.fromtimestamp(record.created).strftime("%f")[0:3])
        return formatted_time


class EvictQueue(queue.Queue):
    # ensures the queue handler cannot consume all available RAM
    def __init__(self, maxsize):
        super().__init__(maxsize)

    def put(self, item, block=False, timeout=None):
        while True:
            try:
                super().put(item, block=False)
                break
            except queue.Full:
                self.get_nowait()


class redirectCustomClass(werkzeug.exceptions.HTTPException):
    description = "/"  # set description to redirect URL


class redirectMovedPermanently(redirectCustomClass):
    # Permanent, POST MAY become GET
    code = 301
    name = "Moved Permanently"


class redirectFound(redirectCustomClass):
    # Temporary, POST MAY become GET
    code = 302
    name = "Found"


class redirectSeeOther(redirectCustomClass):
    # Temporary, POST WILL become GET
    code = 303
    name = "See Other"


class redirectTemporaryRedirect(redirectCustomClass):
    # Temporary, POST WILL NOT become GET
    code = 307
    name = "Temporary Redirect"


class redirectPermanentRedirect(redirectCustomClass):
    # Permanent, POST WILL NOT become GET
    code = 308
    name = "Permanent Redirect"
