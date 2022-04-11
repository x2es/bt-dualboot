from pytest import fixture
import os

#
# EXPERIMENTAL:
# It's hackish for now in order to reuse data context in other tests
#
def unwrap(fn):
    return fn.__pytest_wrapped__.obj


def bt_linux_sample_01_unwrapped():
    return unwrap(bt_linux_sample_01)(unwrap(bt_linux_samples_dir)())


@fixture
def bt_linux_samples_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_samples")


@fixture
def bt_linux_sample_01(bt_linux_samples_dir):
    return os.path.join(bt_linux_samples_dir, "bt_sample_01")
