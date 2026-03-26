"""
Cylinder is a small, opinionated WSGI web framework built on top of werkzeug.

It is designed for developers who want web applications to stay simple,
readable, and predictable. By keeping routing visible in the filesystem and avoiding unnecessary
abstractions, Cylinder makes applications easier to reason about and easier to troubleshoot.

Key features include:

- File-based routing that reflects the URL structure on disk
- Minimal configuration and explicit application wiring
- Support for hooks, custom error handlers, and method-based routing via filenames

Cylinder aims to provide just enough structure to guide development without
hiding how the application works.

"""

import importlib.util
import logging
import logging.handlers
import mimetypes
import os
import pathlib
import queue
import sys
import time
from datetime import datetime
from types import SimpleNamespace
import traceback
from collections import deque

import werkzeug
import werkzeug.local
import werkzeug.test

__author__ = "Chris Wheeler, Nick Gray"
__copyright__ = "Copyright 2026, The Plasma Foundation Inc."
__credits__ = ["Chris Wheeler", "Nick Gray"]
__license__ = "Apache-2.0"
__version__ = "v0.2.2"
__email__ = "Chris Wheeler <grintor@gmail.com>"
__status__ = "Production"


log_queue_length = 1000
werkzeug_local = werkzeug.local.Local()
global_proxy = werkzeug_local("global_proxy")

log_formatter = logging.Formatter(
    "%(levelname)s %(timestamp)s %(filename)s:%(lineno)s %(request_id)s\n    %(message)s\n",
    "%Y-%m-%d %H:%M:%S%z",
)


# ruff: disable[C901, PLR0915]
def get_app(
    app_map,
    log_level=logging.DEBUG,
    log_handler=None,
    request_id_header=None,
    abort_extra=None,
):
    if not callable(app_map):
        raise ValueError("app_map must be a function")

    if not log_handler:
        log_handler = logging.StreamHandler(sys.stderr)

    logger, log_queue, log_listener = configure_logging(
        log_level=log_level,
        log_handler=log_handler,
    )

    def app(environ, start_response):
        request = werkzeug.wrappers.Request(environ, shallow=True)
        werkzeug_local.global_proxy = SimpleNamespace()

        app.abort = werkzeug.exceptions.Aborter(
            extra={
                301: RedirectMovedPermanently,
                302: RedirectFound,
                303: RedirectSeeOther,
                307: RedirectTemporaryRedirect,
                308: RedirectPermanentRedirect,
            }
            | (abort_extra or {})
        )

        global_proxy.param_dict = {
            "request": request,
            "abort": app.abort,
            "logger": logger,
        }

        response = werkzeug.wrappers.Response()

        app_map_response = run_func_with_dict({"response": response} | global_proxy.param_dict, app_map)

        site_dir, site_name, appended_args = (*app_map_response, None)[:3]

        global_proxy.param_dict.update(appended_args or {})

        site_path = pathlib.Path.cwd() / site_dir
        site_root = site_path / site_name
        global_proxy.search_paths = get_search_paths(site_root, request.path)

        global_proxy.site_path = site_path
        global_proxy.start_time = time.time()

        global_proxy.request_id = (
            request.headers.get(request_id_header)
            or f"req_{format(int(global_proxy.start_time * 1000000), 'X')[::-1]}"
        )

        logger.debug(
            "INCOMING_REQUEST: %s %s %s %s",
            request.remote_addr,
            request.method,
            request.url,
            request.environ.get("SERVER_PROTOCOL", ""),
        )

        global_proxy.module_chain = None, None, None
        module = None
        late_hook = None
        try:
            global_proxy.module_chain = get_processors(request.method)
            early_hook, _, late_hook = global_proxy.module_chain
            if not global_proxy.module_chain[1]:
                app.abort(501)

            for module in global_proxy.module_chain:
                shallow_request = module is early_hook
                response = process_module(
                    module, response, global_proxy.param_dict, logger, shallow_request
                )
            return response(environ, start_response)

        except HTTPRedirect as e:
            global_proxy.param_dict.update({"e": e})
            logger.debug("abort redirect %s raised.", e.code)
            response = werkzeug.wrappers.Response("", e.code, {"Location": e.description})

            if module and module is late_hook:
                return response(environ, start_response)

            if late_hook:
                response = process_module(
                    late_hook,
                    response,
                    global_proxy.param_dict,
                    logger,
                )

            return response(environ, start_response)

        except (
            werkzeug.exceptions.HTTPException,
            werkzeug.exceptions.InternalServerError,
        ) as ex:
            global_proxy.param_dict.update({"e": ex})
            response = ex.get_response()
            ex_code = response.status_code
            logger.debug("abort code %s raised.", ex_code)
            custom_handler = get_http_error_handler(ex_code)
            if not custom_handler:
                logger.debug("no custom handler registered for error %s", ex_code)
                if ex_code == 500:  # noqa: PLR2004
                    logger.error("".join(traceback.format_exception(ex)))
            else:
                try:
                    response = process_module(
                        custom_handler,
                        response,
                        global_proxy.param_dict,
                        logger,
                    )
                except werkzeug.exceptions.InternalServerError as e:
                    # an exception in the exception handler becomes a 500 error
                    global_proxy.param_dict.update({"e": e})
                    custom_handler = get_http_error_handler(500)
                    if not custom_handler:
                        logger.error("".join(traceback.format_exception(e)))
                    response = process_module(
                        custom_handler,
                        e.get_response(),
                        global_proxy.param_dict,
                        logger,
                    )

            if module and module is late_hook:
                return response(environ, start_response)

            if late_hook:
                response = process_module(
                    late_hook,
                    response,
                    global_proxy.param_dict,
                    logger,
                )

            return response(environ, start_response)

        finally:
            logger.info(
                "%s %s %s %s | %s | request completed in %s ms",
                request.remote_addr,
                request.method,
                request.url,
                request.environ.get("SERVER_PROTOCOL", ""),
                response.status,
                round((time.time() - global_proxy.start_time) * 1000),
            )

            if app.wait_for_logs:
                app.log_queue.join()

    def test_client():
        return werkzeug.test.Client(app)

    app.logger = logger
    app.log_queue = log_queue
    app.wait_for_logs = False
    app.test_client = test_client
    app.global_proxy = global_proxy

    logger.debug("Plasma cylinder energized. Awaiting requests.")

    return app


def configure_logging(log_level, log_handler):
    log_queue = getattr(configure_logging, "log_queue", None)
    log_listener = getattr(configure_logging, "log_listener", None)

    if log_listener:
        log_listener.stop()

    log_queue = EvictQueue(log_queue_length)
    log_handler.setFormatter(log_formatter)

    log_listener = logging.handlers.QueueListener(log_queue, log_handler)
    log_listener.start()

    logger = logging.getLogger("cylinder")
    logger.propagate = False
    logger.setLevel(log_level)
    logger.handlers.clear()
    logger.addHandler(CustomQueueHandler(log_queue))

    setattr(configure_logging, "log_queue", log_queue)
    setattr(configure_logging, "log_listener", log_listener)

    return logger, log_queue, log_listener


def process_module(module, response, params, logger, shallow_request=False):
    params.update({"response": response})
    if not module:
        return response
    request = params["request"]
    request.shallow = shallow_request
    logger.debug("passing request to %s", module.__name__)
    start_time = time.time()
    try:
        response = validate_response(response, run_func_with_dict(params, module.main))
    except Exception as e:
        if isinstance(e, werkzeug.exceptions.HTTPException):
            raise e
        else:
            raise werkzeug.exceptions.InternalServerError(original_exception=e)
    ms = round((time.time() - start_time) * 1000)
    logger.debug("%s completed in %s ms", module.__name__, ms)
    return response


def validate_response(response_in, response_out):
    if response_out is not response_in:
        raise ValueError("must return the same response passed in")
    return response_out


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
    try:
        if http_method == "DEFAULT":
            raise ValueError('custom HTTP method "DEFAULT" is reserved')
        if not http_method.isalpha():
            raise ValueError("only alpha HTTP methods are supported")

        lower_method = http_method.lower()

        early_hook = get_module(find_processor_path([f"eh.{lower_method}", "eh.default"]))

        direct_path = global_proxy.search_paths[0]
        if (
            http_method == "GET"
            and os.path.isfile(direct_path)
            and not str(direct_path).endswith((".py", ".pyc"))
            and str(pathlib.Path(direct_path).resolve()) == str(direct_path)
        ):
            processor = DirectFileServe
        else:
            processor = get_module(find_processor_path([f"ex.{lower_method}", "ex.default"]))

        late_hook = get_module(find_processor_path([f"lh.{lower_method}", "lh.default"]))

        return (early_hook, processor, late_hook)

    except Exception as e:
        raise werkzeug.exceptions.InternalServerError(original_exception=e)


def find_processor_path(suffix_list):
    for path in global_proxy.search_paths:
        for suffix in suffix_list:
            potential_file = f"{path}.{suffix}.py"
            # pathlib .resolve() is here to handle the case-insensitivity of windows. Enforces case to match
            if (
                os.path.isfile(potential_file)
                and str(pathlib.Path(potential_file).resolve()) == potential_file
            ):
                return potential_file
    return None


def get_search_paths(site_path, url_path_str):
    url_path_str = url_path_str.replace("\\", "/")  # path traversal protection
    part_list = url_path_str.strip("/").split("/")
    results = deque()
    results.append(site_path)
    for part in part_list:
        if part and part != "..":  # path traversal protection
            results.insert(0, results[0] / part)
    return results


def run_func_with_dict(input_dict, func):
    arg_count = func.__code__.co_argcount
    var_names = func.__code__.co_varnames
    params = var_names[:arg_count]
    input_list = []
    for param in params:
        input_list.append(input_dict.get(param, None))
    return func(*input_list)


class DirectFileServe:
    @staticmethod
    def main(response):
        direct_path = global_proxy.search_paths[0]
        mimetype, content_encoding = mimetypes.guess_type(direct_path, strict=False)
        response.content_encoding = content_encoding or "identity"
        response.mimetype = mimetype or "application/octet-stream"
        response.headers["Content-Length"] = os.path.getsize(direct_path)
        response.response = read_file_in_chunks(direct_path)
        return response


def read_file_in_chunks(file_path, chunk_size=16384):
    with open(file_path, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            yield data


class CustomQueueHandler(logging.handlers.QueueHandler):
    # Extend QueueHandler to attach request context to record since
    # request context won't be available inside listener thread.

    def prepare(self, record):
        try:
            record.request_id = global_proxy.request_id
        except Exception:
            record.request_id = ""

        dt = datetime.fromtimestamp(record.created).astimezone()
        record.timestamp = dt.isoformat(timespec="microseconds")

        return record


class EvictQueue(queue.Queue):
    # drops oldest items when full
    def put(self, item, block=False, timeout=None):
        while True:
            try:
                super().put(item, block=False)
                return
            except queue.Full:
                _ = self.get_nowait()
                self.task_done()


class HTTPRedirect(werkzeug.exceptions.HTTPException):
    description = "/"  # set description to redirect URL destination
    name = "HTTPRedirect"


class RedirectMovedPermanently(HTTPRedirect):
    code = 301


class RedirectFound(HTTPRedirect):
    code = 302


class RedirectSeeOther(HTTPRedirect):
    code = 303


class RedirectTemporaryRedirect(HTTPRedirect):
    code = 307


class RedirectPermanentRedirect(HTTPRedirect):
    code = 308
