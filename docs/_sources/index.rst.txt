Plasma Cylinder
================

Plasma Cylinder is a web application framework and webserver built atop `flask`_ and `waitress`_. It is designed to be
production-ready, extraordinarily easy to learn, and to encourage a project layout which facilitates collaboration.


Features
---------

Plasma Cylinder is designed to allow web application to grow organically while remaining manageable. Similar to PHP
on Apache, inbound requests are routed to to the file in the webroot who's path corresponds to the path in the URL.
Unlike PHP on Apache, POST requests are routed to different files than GET requests, keeping logic better segmented
and minimizing the chance of a merge conflict when multiple contributors are working together. Also unlike Apache,
there is no separation between between configuration syntax and code. The server is configured purely in python,
keeping configuration simple yet powerful.

Also unlike PHP, initialization of resources can persist across requests
without needing a plugin. Any objects created in init.py are persistently accessible across all requests. (such as
database connections). In certain situations, this can really speed things up.

Since Plasma Cylinder is based on Flask, it serves a `WSGI`_ web application. This means is can be deployed to AWS
lambda using `Zappa`_. And since it uses waitress for it's server component rather than `werkzeug`_, the same
development environment can be used in production directly.


Getting started
----------------

Simply install Plasma Cylinder with ``pip install cylinder`` and create the required minimum directory structure.

A minimum viable web app looks like this:

.. code-block:: text

    ~/my_server
        |-- myserver.py
        |-- /my_webapps
            |-- init.py
            |-- webapp1.py

here is ``myserver.py``:

.. code-block:: python

    import cylinder # pip install cylinder


    def main():
        app = cylinder.get_app(triage)
        app.run(host="127.0.0.42", port=80)


    def triage(request):
        # here you can examine the incoming request and decide to route to different webapps
        # depending on the hostname for example

        return "my_webapps", "webapp1"


    if __name__ == "__main__":
        main()



here is ``webapp1.py``:

.. code-block:: python

    def main(response):
        response.data = 'Hello World!'
        return response


here is ``init.py``:

.. code-block:: python

    # init is empty for now

Full and more complex examples can be found in the ``examples`` directory in the repository.

Contributing
------------

Pull requests welcome. Please read :ref:`the contributing guide <general/contributing:Contributing to Plasma Cylinder>`



.. _`werkzeug`: https://werkzeug.palletsprojects.com/en/2.1.x/serving/
.. _`Zappa`: https://github.com/zappa/Zappa
.. _`WSGI`: https://wsgi.readthedocs.io/en/latest/
.. _`flask`: https://github.com/pallets/flask
.. _`waitress`: https://github.com/Pylons/waitress
