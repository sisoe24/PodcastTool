#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from podcasttool.skeleton import fib

__author__ = "virgil_sisoe"
__copyright__ = "virgil_sisoe"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
