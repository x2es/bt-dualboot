from pytest import fixture
import os
from tests.helpers import pytest_unwrap

#
# EXPERIMENTAL:
# It's hackish for now in order to reuse data context in other tests
#


def bt_linux_sample_01_unwrapped():
    return pytest_unwrap(bt_linux_sample_01)(pytest_unwrap(bt_linux_samples_dir)())


@fixture
def bt_linux_samples_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_samples")


@fixture
def bt_linux_sample_01(bt_linux_samples_dir):
    return os.path.join(bt_linux_samples_dir, "bt_sample_01")
