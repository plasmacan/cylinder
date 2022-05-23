import os
import sys

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import is_complex  # pylint: disable=wrong-import-position


def test_complex():
    assert is_complex.f10(2) == 2
    assert is_complex.f10(3) == 3
    assert is_complex.f10(4) == 4
    assert is_complex.f10(5) == 5
    assert is_complex.f10(6) == 6
    assert is_complex.f10(7) == 7
    assert is_complex.f10(8) == 8
    assert is_complex.f10(9) == 9
    assert is_complex.f10(10) == 10
    assert is_complex.f10(11) == 11
