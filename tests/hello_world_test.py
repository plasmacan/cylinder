import os
import sys

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import hello_world  # pylint: disable=wrong-import-position


def test_hello_world():
    assert hello_world.function1() == "hello world"
