Contributing to Plasma Cylinder
======================================

Plasma Cylinder uses `pre-commit`_ to enforce the the coding standards. This is enforced in CI, but should be set up
locally as well.

Minimum system requirements are:

* Java 8
* Ruby 2.7
* Python 3.7

After installing the prerequisites, enter the repo directory and create a new python virtual environment
using ``python -m venv venv``

Enter the virtual environment using ``./venv/Scripts/activate``
(or ``.\venv\Scripts\activate`` on windows)

From within the virtual environment, install the requirements ``pip install -r requirements.txt``

Now, set up the pre-commit hook using ``pre-commit install``

To confirm all of the hooks work, run ``pre-commit run -a``

Before pushing, make sure to run ``pytest``. Running that command will not only perform all of the functional tests,
but will also build a test copy of the documentation (this documentation: which you are reading now) and produce a
beautiful HTML coverage report. Both of these will be located in the ``.repo-reports`` directory.

Pytest is also run in CI. A failing test will block a merge, so make sure the tests are passing before making a
pull request.

.. _`pre-commit`: https://github.com/pre-commit/pre-commit
