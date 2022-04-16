def pytest_unwrap(fn):
    return fn.__pytest_wrapped__.obj
