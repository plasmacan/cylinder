# Cylinder

Cylinder is a small, opinionated WSGI web framework built on
[Werkzeug](https://werkzeug.palletsprojects.com/en/2.1.x/serving/). It is designed for developers who want
web applications to stay simple, readable, and predictable.

Instead of layering on a large stack of framework abstractions, Cylinder builds on Werkzeug’s proven HTTP
and WSGI foundations and adds structure through file-based routing. It aims to sit between the two common
extremes: less ad hoc than a microframework, but lighter and more transparent than a full stack framework.

The goal is straightforward: make it easy to understand how requests flow through an application, keep the
project structure visible in the filesystem, and minimize setup and boilerplate.

Plasma is the nonprofit software foundation that supports the ongoing development of Cylinder.
[The Plasma Foundation Inc.](https://www.guidestar.org/profile/88-3345768) is a 501(c)(3) founded by
[Tier2 Technologies](http://tier2.tech/) to support software that benefits the world at large.

## Philosophy

Most Python web frameworks make a tradeoff:

-   **microframeworks** stay out of your way, but leave project structure and conventions up to each team
-   **full stack frameworks** provide structure, but often bring layers, conventions, and abstractions you
    may not want

Cylinder is designed to sit in the middle.

It builds on [Werkzeug](https://werkzeug.palletsprojects.com/en/2.1.x/serving/) because Werkzeug already
solves the underlying HTTP and WSGI problems well: request and response objects, routing primitives,
exceptions, and the general mechanics of web applications. Instead of rebuilding that foundation, Cylinder
uses it directly and adds a simpler application structure on top.

Its main opinionated choice is **file-based routing**.

With file-based routing, the shape of the application is visible in the filesystem. You can look at a
project tree and quickly understand what URLs exist, where their handlers live, and request-response flow.
That lowers mental overhead, makes onboarding easier, and keeps growing codebases easier to navigate.

It also reduces boilerplate. You do not need to maintain a separate routing table, scatter route
declarations across the codebase, or introduce extra layers just to map URLs to code. The directory
structure itself becomes part of the API surface.

By staying close to Werkzeug, Cylinder keeps its internals understandable. By using file-based routing, it
adds convention without hiding control flow.

## Quickstart

Install Cylinder and a WSGI server:

```bash
pip install cylinder waitress
```

A minimal Cylinder app looks like this:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
```

In this example, `cylinder_main.py` creates the WSGI app and tells Cylinder which webapp should handle each
request:

```python
import cylinder
import waitress

def main():
    app = cylinder.get_app(app_map)
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request):
    # Inspect the incoming request here if you want to choose
    # between multiple webapps based on hostname, headers, etc.

    # app_map() returns a tuple of two or three items:
    # 1) site_dir:  the root directory containing your webapps
    # 2) site_name: the webapp that should handle this request
    # 3) optionally: any extra parameters on `main()`
    return "my_webapps", "webapp1"

if __name__ == "__main__":
    main()
```

The file `webapp1.ex.get.py` handles `GET /`:

```python
def main(response):
    response.data = "Hello World!"
    return response
```

Start the app by running `cylinder_main.py`, then visit `http://127.0.0.1`. You should see:

```text
Hello World!
```

## Routing basics

### Implementing pages

In the example above, `webapp1.ex.get.py` handles `GET /`, but because it sits at the root of the webapp it
will also handle deeper paths unless a more specific handler exists.

That means a request to `http://127.0.0.1/foo/bar` would still return `Hello World!` until you add a more
specific file for that route.

To implement a custom `/foo/bar` page, create a file that matches that path:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
        |-- /webapp1
            |-- /foo
                |-- bar.ex.get.py
```

Here is `bar.ex.get.py`:

```python
def main(response):
    response.data = "Hello Bar!"
    return response
```

Now a request to `http://127.0.0.1/foo/bar` will return:

```text
Hello Bar!
```

### Why there are no index files

Many web frameworks and file-based routers revolve around names like `index.html`, `index.php`, or
`page.tsx`.

Cylinder intentionally does not.

One reason is readability. In larger projects, repeated index-style filenames tend to create “index soup”:
you open several tabs in your editor and they all have the same name, even though they represent completely
different routes.

Cylinder avoids that by naming each handler after the final path segment it handles. That keeps route
structure visible in the filesystem while also making files easier to recognize in an editor.

For example, if you are working on `/api/v2/reports/company/payments`, the relevant handlers might look
like this:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
        |-- /webapp1
            |-- /API
                |-- /v2
                    |-- reports.ex.get.py
                    |-- /reports
                        |-- company.ex.get.py
                        |-- /company
                            |-- payments.ex.get.py
```

In this example, only `GET` handlers are shown. If you also wanted to support
`PUT /api/v2/reports/company/payments`, you could add `payments.ex.put.py` in the same directory, or use
`payments.ex.default.py` if you want one file to handle multiple methods.

The important thing to notice is that there is no `index.ex.get.py`, because there does not need to be.

In Cylinder, a route segment can correspond to both a directory and a file. So even though
`/reports/company` corresponds to a `company` directory inside `/reports`, it can also be handled by
`company.ex.get.py` in that same location.

This keeps filenames meaningful without giving up nested route structure.

### HTTP method routing

Cylinder uses the filename to determine both the type of handler and the HTTP method it responds to.

In `bar.ex.get.py`:

-   `.ex` means this is a standard executable page handler (and not a [hook](#hooks))
-   `.get` means it handles `GET` requests

So if you want `/foo/bar` to handle `POST` requests as well, you would add a second file named
`bar.ex.post.py`.

Cylinder is not limited to the standard HTTP methods. If your application uses a custom method, a file such
as `bar.ex.move.py` will handle `MOVE /foo/bar`.

You can also provide a catch-all handler using `.default`. A file named `bar.ex.default.py` will handle any
method for `/foo/bar` that does not have a more specific match.

For example:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
        |-- /webapp1
            |-- /foo
                |-- bar.ex.get.py      <== handles: GET /foo/bar
                |-- bar.ex.post.py     <== handles: POST /foo/bar
                |-- bar.ex.default.py  <== handles: PUT, DELETE, HEAD /foo/bar
```

Meanwhile, `webapp1.ex.get.py` continues to handle `GET` requests everywhere else that does not have a more
specific match.

To behave like a typical web app and return 404 responses for any unimplemented pages, you could edit
`webapp1.ex.get.py` like so:

```python
def main(request, response, abort):
    if request.path != "/": abort(404)
    response.data = "Hello World!"
    return response
```

More details about the abort() function are documented in the [abort()](#abort) section below.

### How requests are matched

When a request comes in, Cylinder chooses the most specific match available on disk.

In practice, the matching rules are:

1.  More specific paths win over less specific paths.
2.  For the same path, an exact method match wins over `.default`.
3.  Static files are served only on an exact path match.
4.  Early hooks run before the selected page or static-file response.
5.  Late hooks run after the selected page or static-file response.
6.  If the request raises an HTTP exception or an uncaught exception, the matching error handler for that
    status code is used.

A few examples make this easier to see.

Given this layout:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
        |-- webapp1.400.py
        |-- /webapp1
            |-- foo.eh.get.py
            |-- foo.ex.default.py
            |-- foo.lh.get.py
            |-- /foo
                |-- bar.ex.get.py
                |-- bar.ex.post.py
                |-- bar.txt
                |-- bar.400.py
```

The following requests would match like this:

-   `GET /foo/bar` → `bar.ex.get.py`
-   `POST /foo/bar` → `bar.ex.post.py`
-   `PUT /foo/bar` → `foo.ex.default.py`
-   `GET /foo/bar.txt` → the static file `bar.txt`
-   `GET /anything-else` → `webapp1.ex.get.py`

Because there is no bar.ex.put.py, Cylinder falls back up the directory tree to the nearest matching
fallback handler, which in this case is foo.ex.default.py.

For `GET /foo/bar`, the full flow would be:

1.  `foo.eh.get.py`
2.  `bar.ex.get.py`
3.  `foo.lh.get.py`

If `bar.ex.get.py` calls `abort(400)`, Cylinder would then use the most specific matching `400` handler:

1.  `foo.eh.get.py`
2.  `bar.ex.get.py`
3.  `bar.400.py`
4.  `foo.lh.get.py`

If there were no `bar.400.py`, then `webapp1.400.py` would handle that error instead.

The main idea is simple: Cylinder prefers the most specific file available for the request, and then
applies hooks and error handlers around that choice.

### Static files

Cylinder can also serve static files directly from the filesystem.

For example:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
        |-- webapp1.500.py
        |-- /webapp1
            |-- example1.json
            |-- foo.400.py
            |-- /foo
                |-- example2.css
```

In this layout:

-   a request to `/example1.json` returns the contents of `example1.json`
-   a request to `/foo/example2.css` returns the contents of `example2.css`

Cylinder sets the `Content-Type` header based on the file extension using Python’s standard library
[`mimetypes`](https://docs.python.org/3/library/mimetypes.html). In the example above, the responses would
use `application/json` and `text/css` respectively.

Static files are served only when the URL path matches the file path exactly. Python source files are never
served.

Static file responses still pass through the normal hook system, so early hooks and late hooks can inspect
or modify the response just as they can for page handlers.

### Dynamic paths / dynamic route handling

Not every URL has a simple 1:1 relationship with the filesystem.

For example, in a REST API you might expect:

-   `POST /API/v1/users` to create a user and return an ID
-   `GET /API/v1/users/<id>` to return a specific user
-   `GET /API/v1/users?lname=Smith` to search for users by last name
-   `PUT /API/v1/users/<id>` to update a specific user
-   `DELETE /API/v1/users/<id>` to delete a specific user

Cylinder does not use named dynamic route declarations. Instead, it matches each request to the most
specific handler on disk, and any remaining path information stays available on the request object for your
application code to interpret.

A layout for the example above might look like this:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
        |-- /webapp1
            |-- /API
                |-- v1.ex.default.py
                |-- /v1
                    |-- users.ex.post.py
                    |-- users.ex.get.py
                    |-- users.ex.put.py
                    |-- users.ex.delete.py
```

In this layout:

-   `POST /API/v1/users` is handled by `users.ex.post.py`
-   `GET /API/v1/users` is handled by `users.ex.get.py`
-   `PUT /API/v1/users/<id>` is handled by `users.ex.put.py`
-   `DELETE /API/v1/users/<id>` is handled by `users.ex.delete.py`

The important point is that Cylinder routes the request to the most specific matching handler file. It does
not matter that `/users/<id>` contains dynamic path data after `/users`; that remaining path can be
interpreted by your handler code using the request object.

For example, a `HEAD` request to `/API/v1/users` would be handled by `v1.ex.default.py`, because there is
no more specific `HEAD` handler for that route. A `GET` request to `/API/v1/users` would still be handled
by `users.ex.get.py`.

#### Accessing the remaining path

Cylinder does not parse dynamic path segments into named route parameters for you.

Instead, your handler receives the normal Werkzeug `request` object, and you can inspect the request path
directly and interpret any remaining segments however your application needs.

For example, with this layout:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
        |-- /webapp1
            |-- /API
                |-- /v1
                    |-- users.ex.get.py
```

a `GET` request to `/API/v1/users` and a request to `/API/v1/users/123` would both be handled by
`users.ex.get.py`.

Inside that handler, you can examine `request.path` and parse the remainder yourself:

```python
def main(request, response):
    path = request.path.rstrip("/")
    parts = path.split("/")

    if len(parts) == 4:
        # /API/v1/users
        response.data = "list users"
    elif len(parts) == 5:
        # /API/v1/users/123
        user_id = parts[4]
        response.data = f"get user {user_id}"
    else:
        response.status_code = 404
        response.data = "not found"

    return response
```

Query string parameters continue to work normally through Werkzeug as well:

```python
def main(request, response):
    last_name = request.args.get("lname")
    response.data = f"searching for lname={last_name}"
    return response
```

The important point is that Cylinder handles selecting the correct file, while your application code
remains responsible for interpreting any dynamic data that comes after that match.

## Request lifecycle

### The request and response objects

Each page module implements a `main()` function. The most important object passed into that function is
`response`:

```python
def main(response):
    response.data = "Hello World!"
    return response
```

`response` is an empty
[Werkzeug Response](https://werkzeug.palletsprojects.com/en/stable/wrappers/#werkzeug.wrappers.Response)
object that Cylinder creates for you before calling your handler. Your job is to modify it as needed and
return it.

For example, you might set:

-   `response.data` for the response body
-   `response.status_code` for the HTTP status
-   `response.content_type` for the content type
-   `response.headers[...]` for custom headers

If your handler also needs access to the incoming request, include a `request` parameter:

```python
def main(request, response):
    response.data = f"Hello {request.user_agent}!"
    return response
```

`request` is the corresponding
[Werkzeug Request](https://werkzeug.palletsprojects.com/en/stable/wrappers/#werkzeug.wrappers.Request)
object, so you can inspect headers, query parameters, form data, cookies, the path, and anything else
Werkzeug exposes.

If you visit the page in a browser, the response would look something like:

```text
Hello Mozilla/5.0 (...)
```

The order of the parameters does not matter. For example, `main(response, request)` works the same way as
`main(request, response)`.

### Handler Parameters

Each page file is a normal Python module, and each handler is a normal Python function named `main()`. You
can define other helper functions of course, as with any Python module.

Cylinder calls that function by importing the module and then passing in any supported parameters that your
handler asks for. The only required parameter is `response`, but a few others are available as well:

```python
def main(request, response, logger, abort):
    logger.info("Saying hello to %s", request.user_agent)
    response.data = f"Hello {request.user_agent}!"
    return response
```

The built-in parameters are:

-   `response` — the
    [Werkzeug Response](https://werkzeug.palletsprojects.com/en/stable/wrappers/#werkzeug.wrappers.Response)
    object your handler should modify and return
-   `request` — the
    [Werkzeug Request](https://werkzeug.palletsprojects.com/en/stable/wrappers/#werkzeug.wrappers.Request)
    object for the current request
-   `logger` — Cylinder’s logger for the current request
-   `abort` — the
    [Werkzeug `abort()` function](https://werkzeug.palletsprojects.com/en/stable/exceptions/#simple-aborting),
    extended with support for redirect-style HTTP exceptions such as `301`, `302`, `303`, `307`, and `308`
-   `e` — the exception object, available only in exception handlers

You do not need to declare parameters you are not using. Cylinder only passes the ones your `main()`
function asks for.

These are the built-in parameters provided by the framework.

`app_map()` can receive the same built-in framework parameters as page handlers, in any order.

The most common form is `app_map(request)`, but you can include the others if you need them:

```python
def app_map(request, response, logger, abort):
    ...
```

You can also define your own extra parameters in `app_map()`,
[as covered later](#extra-parameters-on-main). Before that, it helps to understand how `abort()` and
exception handlers work.

### Hooks

Cylinder supports two kinds of hooks:

-   `early hooks`, which run before the main page handler
-   `late hooks`, which run after the main page handler

Hooks are defined the same way as page handlers: by placing files in the filesystem with special
extensions.

For example:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
        |-- /webapp1
            |-- /API
                |-- v2.lh.get.py
                |-- /v2
                    |-- reports.eh.get.py
                    |-- reports.ex.get.py
                    |-- /reports
                        |-- company.ex.get.py
                        |-- /company
                            |-- payments.ex.get.py
                    |-- users.ex.get.py
```

In this layout:

-   `v2.lh.get.py` is a late hook for requests under `/API/v2/*`
-   `reports.eh.get.py` is an early hook for requests under `/API/v2/reports/*`

So a `GET` request to `/API/v2/reports/company/*` would flow like this after `app_map()`:

1.  `main()` in `reports.eh.get.py`
2.  `main()` in `company.ex.get.py`
3.  `main()` in `v2.lh.get.py`

A `GET` request to `/API/v2/users` would flow like this instead:

1.  `main()` in `users.ex.get.py`
2.  `main()` in `v2.lh.get.py`

Hooks use the same `main()` function pattern as normal page handlers, and they can receive the same
parameters.

Their main purpose is to avoid repetition by letting shared logic run across a directory subtree. Common
examples include authentication checks, loading shared request data, setting default headers, or enforcing
response policies.

Early hooks are a good place to set defaults before the page handler runs. Late hooks are a good place to
enforce final response behavior, because they run after the page handler and get the last word.

For example, if `v2.lh.get.py` contains:

```python
def main(response):
    response.headers["Content-Security-Policy"] = "default-src 'self';"
    return response
```

then a different `Content-Security-Policy` set earlier in `company.ex.get.py` would be overwritten by the
late hook.

## Error handling

### abort()

The
[`abort()` function in Werkzeug](https://werkzeug.palletsprojects.com/en/stable/exceptions/#simple-aborting)
works by raising an HTTP exception. If that exception is not handled by one of your own error handler
files, Werkzeug will generate a default response for it.

For example:

```python
def main(response, abort):
    abort(400)
```

A request to that page would return Werkzeug’s default `400 Bad Request` response, something like:

```html
<html>
    <h1>Bad Request</h1>
    The browser (or proxy) sent a request that this server could not understand.
</html>
```

You can also provide a custom description:

```python
def main(response, abort):
    abort(400, "Something went wrong")
```

That would produce a response more like:

```html
<html>
    <h1>Bad Request</h1>
    Something went wrong
</html>
```

This is often good enough for simple HTML responses, but many applications need more control than that. For
example, a JSON API usually should not return an HTML error page for a `400` response.

That is where [exception handler files](#exception-handlers) come in.

### Exception handlers

Cylinder lets you customize HTTP errors by creating handler files named after the status code.

For example:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
        |-- webapp1.400.py
        |-- /webapp1
            |-- /foo
                |-- bar.ex.get.py
```

In this layout, `webapp1.400.py` handles `400` errors for the site.

When code calls `abort(400)`, or otherwise raises a `400` HTTP exception, Cylinder passes control to that
file’s `main()` function. From there, you can build whatever response you want instead of relying on
Werkzeug’s default error page.

Exception handlers can also receive the optional `e` parameter, which is the exception object that was
raised. This can be useful for logging, debugging, auditing, or building structured API responses.

For example, `webapp1.400.py` might look like this:

```python
import json
import traceback

def main(request, response, e, logger):
    tb_str = "".join(traceback.format_exception(e))
    logger.error("Got a 400 error: %s", tb_str)
    response.content_type = "application/json; charset=UTF-8"
    response.data = json.dumps({
        "message": "bad_request",
        "status": 400,
        "error": True,
    })
    return response
```

Exception handlers are also a good place for error-related post-processing. For example, you might log
repeated `404` responses by IP address as part of bot detection, trigger alerts on certain classes of
failures, or normalize all API errors into a consistent JSON format.

Error handlers can also be scoped by path, just like normal page handlers.

For example:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
        |-- webapp1.400.py
        |-- /webapp1
            |-- foo.400.py
            |-- /foo
                |-- bar.ex.get.py
```

In this layout:

-   `webapp1.400.py` handles `400` errors for the site in general
-   `foo.400.py` handles `400` errors under `/foo/*`

This makes it easy to return HTML error pages for most of a site while returning JSON errors for a specific
subtree such as `/api/`.

### Uncaught Exceptions

Uncaught exceptions are treated as `500 Internal Server Error` responses.

For that reason, you generally should not call `abort(500)` yourself. If you need to signal an expected
failure, use the most specific status code that fits the situation, such as `501` or `503`, or a custom
status code with [abort_extra](#abort_extra)

When an unhandled exception occurs, Cylinder routes it to your `500` error handler if one exists. In that
handler, the `e` parameter will be a
[Werkzeug `InternalServerError`](https://werkzeug.palletsprojects.com/en/stable/exceptions/#werkzeug.exceptions.InternalServerError),
and its `.original_exception` attribute will contain the actual uncaught exception.

For example:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.ex.get.py
        |-- webapp1.500.py
        |-- /webapp1
            |-- foo.400.py
            |-- /foo
                |-- bar.ex.get.py
```

In this layout, `webapp1.500.py` handles uncaught exceptions for the site.

You can use a `500` handler to log tracebacks, send alerts, or return a custom error response. For example,
this handler returns the traceback as plain text:

```python
import traceback

def main(response, e):
    tb_str = "".join(traceback.format_exception(e.original_exception))
    response.content_type = "text/plain; charset=UTF-8"
    response.data = tb_str
    return response
```

That can be useful while developing, but in production you would usually log the traceback and return a
more generic response instead.

### abort_extra

`abort_extra` is an optional argument to `get_app()` that lets you register additional HTTP exception
classes beyond the ones
[Werkzeug provides by default](https://werkzeug.palletsprojects.com/en/stable/exceptions/#custom-errors).

This extends both `abort()` and the corresponding error-handler file mechanism.

For example, if you want to support `507 Insufficient Storage`, you can define your own exception class and
pass it in through `abort_extra`:

```python
import cylinder
import waitress
import werkzeug

class InsufficientStorage(werkzeug.exceptions.HTTPException):
    code = 507
    name = "Insufficient Storage"
    description = "The server has insufficient storage to complete the request"

def main():
    app = cylinder.get_app(
        app_map,
        abort_extra={507: InsufficientStorage},
    )
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request):
    return "my_webapps", "webapp1"

if __name__ == "__main__":
    main()
```

Once that is configured, calling `abort(507)` anywhere in your handlers will raise that exception.

If you do not provide a custom `507` error handler, the response will use your exception’s defined name,
description, and status code to return a simple HTML page.

If you do provide a matching error handler file such as `webapp1.507.py`, Cylinder will route the request
through that handler and let you customize the response just like any other HTTP error.

### Redirects

Cylinder also supports redirects through `abort()`.

The built-in redirect codes are `301`, `302`, `303`, `307` and `308`

The second argument to `abort()` is the redirect target, for example:

```python
def main(request, response, abort):
    if not request.cookies.get("session_id"):
        abort(302, "/login")
```

Redirects do not use `301.py`, `302.py`, and similar [exception handler files](#exception-handlers).
Cylinder handles the redirect automatically.

Late hooks still run unless the redirect is raised from the late hook itself, so late hooks can still
modify headers on redirect responses.

## Application composition

### Extra parameters on `main()`

In addition to the built-in parameters provided by the framework (`request`, `response`, `logger`, `abort`,
and, in exception handlers, `e`), your handlers can also receive arbitrary extra parameters defined by your
application.

These extra parameters come from an optional third value in the tuple returned by `app_map()`.

That third value is a dictionary where you define any additional objects, helpers, or application resources
you want Cylinder to make available to your page modules.

If, for example, you want to make Python’s `json` module available throughout the app, you can pass it
through `app_map()`:

```python
import cylinder
import waitress
import json

def main():
    app = cylinder.get_app(app_map)
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request):
    return "my_webapps", "webapp1", {"json": json}

if __name__ == "__main__":
    main()
```

Once that is configured, any page in `webapp1` can ask for `json` as a parameter to `main()`.

Without an extra parameter, you would write:

```python
import json

def main(request, response):
    response.data = json.dumps({
        "message": "hello world",
        "status": 200,
        "error": False,
    })
    return response
```

With `json` provided through `app_map()`, you can instead write:

```python
def main(request, response, json):
    response.data = json.dumps({
        "message": "hello world",
        "status": 200,
        "error": False,
    })
    return response
```

This same mechanism works for many other kinds of application-level dependencies, such as:

-   configuration objects
-   database session factories
-   template render functions
-   locks
-   helper modules
-   aliases for built-in framework objects

For example, if you prefer the shorter `log` over `logger`, you can provide that alias yourself:

```python
import cylinder
import waitress

def main():
    app = cylinder.get_app(app_map)
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request, logger):
    return "my_webapps", "webapp1", {"log": logger}

if __name__ == "__main__":
    main()
```

Then your page modules can use `log` as a parameter instead of `logger`, and write `log.info()` instead of
`logger.info()`.

This is one of Cylinder’s main extension points: built-in request handling from the framework, plus
application-specific dependencies passed in explicitly through `app_map()`.

### Configuration and Environments

Cylinder keeps framework-level configuration intentionally small. The built-in options on `get_app()` are:

```python
def get_app(
    app_map,
    log_level=logging.DEBUG,
    log_handler=None, # defaults to internal stream handler to stderr
    request_id_header=None, # should usually be set to "X-Request-ID"
    abort_extra=None,
):
```

Beyond that, Cylinder treats configuration as ordinary Python code.

Instead of introducing a separate configuration system, Cylinder expects you to express application
behavior directly in `cylinder_main.py`, in `app_map()`, and in your hooks and handlers. That keeps
configuration flexible and close to the code it affects.

For example, routing different hostnames to different webapps works naturally in `app_map()`:

```python
import cylinder
import waitress

def main():
    app = cylinder.get_app(app_map)
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request):
    if request.host == "foo.com":
        return "my_webapps", "foo"
    else:
        return "my_webapps", "bar"

if __name__ == "__main__":
    main()
```

This plays a role similar to Apache virtual hosts or nginx server blocks, but it is expressed directly in
Python.

If you want to load values from a `.env` file, you can do that too and pass the resulting config object
into your handlers:

```python
import cylinder
import waitress
from dotenv import dotenv_values

config = dotenv_values(".env")

def main():
    app = cylinder.get_app(app_map)
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request):
    return "my_webapps", "webapp1", {"config": config}

if __name__ == "__main__":
    main()
```

Configuration can also be applied structurally through hooks.

For example, if you want to set a CORS header across an entire site, you can do that with an early hook at
the root:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /my_webapps
        |-- webapp1.eh.get.py
        |-- webapp1.ex.get.py
        |-- /webapp1
            |-- /API
                |-- /v2
                    |-- reports.ex.get.py
                    |-- /reports
                        |-- company.ex.get.py
                        |-- /company
                            |-- payments.ex.get.py
```

In this example, `webapp1.eh.get.py` could contain:

```python
def main(request, response):
    response.access_control_allow_origin = "*"
    return response
```

Because this early hook is at the root of the site, and there are no more specific hooks overriding it,
that header would be applied throughout the site.

In short, Cylinder does not separate “configuration” from application code very aggressively. Most
configuration is simply expressed in Python, using the same routing, parameter, and hook mechanisms as the
rest of the framework.

### HTML templates and Jinja2

Cylinder does not include a built-in template engine. Instead, template rendering is meant to be added the
same way as any other application dependency: define it in `cylinder_main.py` and pass it in through
`app_map()`.

For example, here is a minimal Jinja2 setup:

```python
import cylinder
import waitress
import jinja2

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
    auto_reload=True,
    autoescape=jinja2.select_autoescape(),
)

def render_template(template_name, **context):
    template = jinja_env.get_template(template_name)
    return template.render(**context)

def main():
    app = cylinder.get_app(app_map)
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request):
    return "my_webapps", "webapp1", {"render_template": render_template}

if __name__ == "__main__":
    main()
```

With that in place, any page module in the app can ask for `render_template` as a parameter to `main()`.

A simple project layout might look like this:

```text
~/cylinder_sites
    |-- cylinder_main.py
    |-- /templates
        |-- hello.html
    |-- /my_webapps
        |-- webapp1.ex.get.py
```

Here is `webapp1.ex.get.py`:

```python
def main(response, render_template):
    response.data = render_template("hello.html", name="Developer")
    response.content_type = "text/html; charset=utf-8"
    return response
```

Here is `hello.html`:

```html
<!doctype html>
<html>
    <body>
        Hello, {{ name }}
    </body>
</html>
```

Visiting `/` will then return:

```text
Hello, Developer
```

This approach keeps Cylinder template-engine agnostic while still making common tools like Jinja2 easy to
integrate.

### databases / SQLAlchemy

Database setup is often verbose enough that it makes sense to keep it in a separate module rather than
inside `cylinder_main.py`.

For example, with SQLAlchemy you might define your engine and session factory in `db.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///app.db")
SessionLocal = sessionmaker(engine)

# models, helpers, and other setup can live here too
```

Then import that module into `cylinder_main.py` and pass the session factory through `app_map()`:

```python
import cylinder
import waitress
import db

def main():
    app = cylinder.get_app(app_map)
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request):
    return "my_webapps", "webapp1", {"SessionLocal": db.SessionLocal}

if __name__ == "__main__":
    main()
```

Once that is in place, any page module in the app can ask for `SessionLocal` as a parameter to `main()`.

SQLAlchemy models and query helpers can be imported normally inside page modules. Stateful objects such as
the engine or session factory are usually better passed in through `app_map()`.

For example:

```python
from sqlalchemy import select
from models import User

def main(response, SessionLocal):
    with SessionLocal() as session:
        users = session.execute(select(User)).scalars().all()
        response.data = f"{len(users)} users found"
    return response
```

The important idea is that shared database objects are initialized once, then passed into handlers
explicitly just like any other application dependency.

### Sessions

Cylinder does not implement sessions for you.

That is intentional. There is no single session design that fits every application well. Some frameworks
store the full session in the browser, which can scale nicely but makes it easy to misuse sessions for
sensitive data. Others store session data on the server and use a session ID cookie, which can be simpler
to reason about but requires shared storage if the application runs on multiple servers.

Cylinder leaves that choice to the developer.

A minimal server-side session implementation might look like this:

```python
import cylinder
import waitress

import json
import secrets
import sqlite3
from collections import UserDict

def main():
    app = cylinder.get_app(app_map)
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request, response):
    session_id = request.cookies.get("session_id") or secrets.token_urlsafe(32)
    response.set_cookie("session_id", session_id, httponly=True) # should also set `secure=True` in production
    session = SessionDict(session_id)
    return "my_webapps", "webapp1", {
        "session": session,
        "session_id": session_id,
    }

class SessionDict(UserDict):
    def __init__(self, uid):
        self.uid = uid
        self.conn = sqlite3.connect("sessions.sqlite")
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS store (uid TEXT PRIMARY KEY, data TEXT)"
        )
        row = self.conn.execute(
            "SELECT data FROM store WHERE uid=?", (self.uid,)
        ).fetchone()
        super().__init__(json.loads(row[0]) if row else {})

    def _save(self):
        self.conn.execute(
            "INSERT OR REPLACE INTO store VALUES (?, ?)",
            (self.uid, json.dumps(self.data)),
        )
        self.conn.commit()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._save()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._save()

if __name__ == "__main__":
    main()
```

You could then use that session in a page module like this:

```python
def main(response, request, session, session_id):
    visits = session.get("visits", 0)
    session["visits"] = visits + 1
    response.data = f"visits: {visits}"
    return response
```

In this example, session data is stored in SQLite and linked to the client through a `session_id` cookie.

If the application later needs to scale beyond a single server, the same pattern can be reused with shared
storage such as PostgreSQL, Redis, or another external system.

You could also, for example, attach session state to [g]{#the-g-object} from an early hook instead of
passing it directly from `app_map()`. That can be useful if different parts of the site need different
cookie or authentication behavior, such as a browser-facing site and a separate `/api` subtree.

### The `g` object

Users coming from Flask may be familiar with the
[Flask `g` object](https://flask.palletsprojects.com/en/stable/appcontext/#storing-data). Cylinder does not
implement the `g` object for you because Cylinder's architecture makes it trivial to do so yourself.

You can create the `g` object like so:

```python
import cylinder
import waitress
from types import SimpleNamespace

def main():
    app = cylinder.get_app(app_map)
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request):
    return "my_webapps", "webapp1", {"g": SimpleNamespace()}

if __name__ == "__main__":
    main()
```

## Operations and development

### Testing

Like [Flask](https://flask.palletsprojects.com/en/stable/testing/#sending-requests-with-the-test-client),
Cylinder exposes a
[Werkzeug test client](https://werkzeug.palletsprojects.com/en/stable/test/#werkzeug.test.Client) as
`app.test_client()`.

Here is a simple example using [pytest](https://docs.pytest.org/en/stable/).

`conftest.py`:

```python
import pytest
import cylinder

@pytest.fixture()
def webapp1_app(caplog):
    def app_map(request):
        return "my_webapps", "webapp1"

    app = cylinder.get_app(app_map, log_handler=caplog.handler)
    app.wait_for_logs = True  # wait for the log queue to drain before returning

    # other setup can go here

    yield app

    # cleanup or reset logic can go here

```

`webapp1_test.py`:

```python
def test_root(webapp1_app, caplog):
    webapp1_client = webapp1_app.test_client()

    response = webapp1_client.get("/")

    assert response.status_code == 200
    assert b"Hello World!" in response.data
    assert response.headers["Access-Control-Allow-Origin"] == "*"

    webapp1_app.log_queue.join()

    assert 'my custom log message' in caplog.text

```

This makes it easy to test Cylinder apps using the same request/response patterns you would use in
production.

### Import caching and reload behavior

Cylinder does not rely on a separate development reload mode for normal page changes.

Page handlers, hooks, and error handlers are loaded dynamically at request time, so changes to those files
are reflected without restarting the application.

This means there is usually no need for a special “development mode” that watches files and reloads the
process when your route logic changes.

The main exception is `cylinder_main.py` itself, or any objects it initializes and keeps around outside of
`app_map()`.

For example, if `cylinder_main.py` imports a module, creates a database engine, builds a template
environment, or otherwise initializes an object once and then passes that object through `app_map()`, that
object will remain cached for the life of the process. Changes to that code will not take effect until the
application is restarted.

In summary:

-   changes to page handlers, hooks, and error handlers are picked up dynamically
-   changes to `cylinder_main.py` require a restart
-   changes to modules or objects initialized once from `cylinder_main.py` also require a restart

In practice, this means most request-handling code behaves dynamically, while application bootstrap code
behaves like normal long-lived Python process state.

### Logging configuration

Cylinder’s built-in logging can be customized through `get_app()` and through the log formatter.

For example, the default formatter looks like this:

```python
import cylinder
import waitress
import logging

cylinder.log_formatter = logging.Formatter(
    "%(levelname)s %(timestamp)s %(filename)s:%(lineno)s %(request_id)s\n    %(message)s\n",
    "%Y-%m-%d %H:%M:%S%z",
)

def main():
    app = cylinder.get_app(app_map)
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request):
    return "my_webapps", "webapp1"

if __name__ == "__main__":
    main()
```

You can replace that formatter with your own if you want different output.

Note the non-standard `request_id` field in the format string. This is described in more detail in
[request_id_header](#request_id_header).

Cylinder’s main logging-related options are:

-   `log_level` — controls the logging level passed to the application logger. It defaults to
    `logging.DEBUG`.
-   `log_handler` — controls where log records are written. By default, Cylinder creates a
    `logging.StreamHandler(sys.stderr)`. You can pass your own handler instead, such as a file handler, an
    SMTP handler, the [pytest caplog handler](#testing), or `logging.NullHandler` if you want to silence
    logs.

Cylinder uses a queue for logging so that request handling does not have to wait on the log handler before
returning a response. This is especially useful when the handler is slow, such as
[`SMTPHandler`](https://docs.python.org/3/library/logging.handlers.html#smtphandler).

### request_id_header

`request_id_header` is an optional argument to `get_app()` that specifies which incoming HTTP header should
be used as the request ID.

It defaults to `None`. If your proxy or CDN provides a header, you should set it. For example, Cloudflare
commonly uses `Cf-Ray`, while the rest of the world uses `X-Request-ID`.

If left unconfigured, or the configured header is missing, Cylinder generates a request ID automatically.

The request ID is included in log records so that all log entries for a single request can be correlated
easily.

### Streaming

#### Streaming response bodies

In some cases, you may want to send a response incrementally instead of building the entire response body
in memory first. This is commonly used for long-running processes, server-sent data, or large outputs.

Cylinder supports streaming by allowing you to assign an iterable (such as a generator) to
`response.response`.

When doing this, you should remove the `Content-Length` header, since the total size of the response is not
known in advance.

For example:

```python
import time

def main(response, logger):
    del response.headers["Content-Length"]
    response.response = fibonacci(logger)
    return response

def fibonacci(logger):
    a, b = 0, 1
    while True:
        time.sleep(0.1)
        logger.info(f"yielding: {a}")
        yield f"{a}\n"
        a, b = b, a + b
```

In this example, the response is streamed to the client one line at a time as values are generated.

Each value yielded by the generator becomes part of the response body. This allows the client to start
receiving data immediately, rather than waiting for the entire response to be constructed.

Streaming responses still pass through hooks in the normal way, but once iteration begins, the response
body is sent progressively as data is yielded.

#### Streaming request bodies

Just as responses can be streamed out, request bodies can also be consumed incrementally.

This is useful for handling large uploads or processing data as it arrives, without loading the entire
request body into memory.

The underlying Werkzeug request exposes the incoming data as a file-like stream via `request.stream`.

For example:

```python
def main(request, response, logger):
    total_bytes = 0

    while True:
        chunk = request.stream.read(4096)
        if not chunk:
            break

        total_bytes += len(chunk)
        logger.info(f"received {len(chunk)} bytes")

    response.data = f"received {total_bytes} bytes"
    return response
```

In this example, the request body is read in chunks of 4096 bytes until the stream is exhausted.

This allows your application to handle large payloads efficiently, process data incrementally, or forward
data to another service without buffering the entire request.

If you access higher-level helpers like `request.data`, `request.form`, or `request.get_json()`, Werkzeug
will read and buffer the full request body for you. To keep streaming behavior, work directly with
`request.stream`.

### Safeguards

Cylinder includes a few small safeguards to make request handling more predictable.

#### Shallow requests in `app_map()` and early hooks

During `app_map()` and early hooks, Cylinder uses the Werkzeug request object in
[shallow](https://werkzeug.palletsprojects.com/en/stable/wrappers/#werkzeug.wrappers.Request.shallow) mode.

In practice, that means code in those stages cannot read the request body through APIs such as:

-   `request.data`
-   `request.form`
-   `request.get_json()`
-   `request.stream.read(...)`

This helps prevent a common class of bugs where shared routing or hook code consumes the request body
before the main page handler gets a chance to use it.

For example, this is a bad fit for an early hook:

```python
def main(request, response):
    payload = request.get_json()
    return response
```

If you need to inspect the request body, do that in the page handler instead.

Access to metadata such as headers, cookies, query parameters, method, host, and path is still fine in
`app_map()` and early hooks.

If you find yourself in a situation where you _need_ to consume the request body early, you can still do so
by setting `shallow` to `False` on the request object:

```python
def main(request, response):
    request.shallow = False
    payload = request.get_json()
    return response
```

#### Handlers must return the same response object

Cylinder creates one `response` object for the request and passes that same object through hooks, page
handlers, and exception handlers.

Your code must modify that object and return it. It should not create and return a different response
object.

For example, this is correct:

```python
def main(response):
    response.data = "Hello World!"
    return response
```

This is not:

```python
from werkzeug.wrappers import Response

def main(response):
    return Response("Hello World!")
```

If a handler returns a different response object, Cylinder raises:

```text
ValueError: must return the same response passed in
```

This rule keeps control flow simpler and makes it easier for hooks and handlers to cooperate on the same
response.

#### Why these rules exist

Both protections are there to reduce surprising behavior:

-   shallow requests help prevent request-body consumption in shared pre-processing code
-   the response identity check helps prevent handlers from silently bypassing earlier changes to the
    response object

The general pattern in Cylinder is:

-   inspect request metadata in `app_map()` and early hooks
-   read the request body in the page handler
-   modify the provided `response` object and return that same object

### Thread safety

Thread safety in Cylinder works the same way it does in any other WSGI application.

Each request may be handled concurrently, depending on the server you are using. The examples in these docs
use [Waitress](https://pypi.org/project/waitress/), which uses multithreading. Other servers may use
multi-processing.

If your application shares state between requests, and that state is not concurrency-safe on its own, you
are responsible for protecting it with the appropriate synchronization primitive such as a lock.

Cylinder makes that easy to do by passing shared objects in through `app_map()`.

For example, in `cylinder_main.py`:

```python
import cylinder
import waitress
import threading

lock = threading.Lock()

def main():
    app = cylinder.get_app(app_map)
    waitress.serve(app, host="127.0.0.1", port=80)

def app_map(request):
    return "my_webapps", "webapp1", {"lock": lock}

if __name__ == "__main__":
    main()
```

Now any page module in the app can ask for that lock as a parameter:

```python
def main(request, response, lock):
    with lock:
        # do something that is not thread-safe
        pass
    return response
```

This pattern is useful for protecting shared in-memory data structures, coordinating access to
non-thread-safe resources, or wrapping code that must not run concurrently.

### Type hints and editor support

Cylinder does not require type hints, but adding them can make development much easier. Most modern editors
(such as VS Code or PyCharm) use type hints to provide:

-   autocomplete suggestions
-   inline documentation
-   error highlighting
-   better navigation

For example, you can annotate `request` and `response` using Werkzeug’s types:

```python
from werkzeug.wrappers import Request, Response

def main(request: Request, response: Response):
    response.data = request.path
    return response
```

This allows your editor to understand what `request` and `response` are, so attributes like `request.args`,
`request.cookies`, or `response.headers` will autocomplete correctly.
