bt-dualboot: Development Guide
==============================

## Development environment

 * [pyenv](https://github.com/pyenv/pyenv#getting-pyenv) with locked Python version by `.python-version` (every testing/deployment tool should respect this version)
 * [docker engine](https://docs.docker.com/engine/install/)
 * [poetry](https://python-poetry.org/docs/#installation) (installed automatically by `dev/bootstrap`)


### Bootstrap

```console
$ git clone git@github.com:x2es/bt-dualboot.git \
    && cd bt-dualboot \
    && dev/bootstrap
```

**NOTE**: `dev/bootstrap` will install poetry unless exist, checkout script code


### Usage

```sh
$ dev/start-tests -w --pdb -x      # unit tests (tests/): watch on code changes, 
                                   # drop to debugger on failure, skip tests after failure
$ dev/start-tests --launcher-help  # checkout pytest_launcher help

# the same for tests_integration/ using Docker containers
$ ONLY_ENV=env_single_windows dev/start-tests-integration -w --pdb -x

# update pytest-snapshot snapshots
$ dev/start-tests-integration --snapshot-update

$ dev/start-tests-manual                     # spawn shell inside Docker container with prepared test set
$ dev/start-tests-all                        # invoke unit & integration tests
$ dev/start-tests-all --flags pre-release    # plus invoke pre-release environments like `pip install`, 
                                             # test over different Python versions and so on
$ dev/pre-release-all                        # overview issues prior release
...
```

### Testing environment

`dev/` directory provides tools which allows manage multiple environments and configurations per environment.

Checkout `tests_integration/cli/env_single_windows/` as example. **Env launcher** `.../start` will be invoked in context of two Docker containers:

* `Dockerfile`: default "for development" environment, with bind-mounted project. Suitable to work in "watch on changes" mode.
* `Dockerfile.pip`: emulates end-user scenario with `pip install` using executable from package

The same tests `.../env_single_windows/test_*.py` will be invoked for both environments.

Both Dockerfiles nests from the `Dockerfile.base`. Project's tests launchers allows build flexible and powerful configurations, nest Docker images, apply multiple variants of options per every Dockerfile, like testsing with different target version of Python.

See for details:
* [dev/start-tests-integration](#devstart-tests-integration-integration-tests-for-multiple-environments)
* [multiple Dockerfiles (contexts) per environment](#multiple-dockerfiles-contexts-per-environment)
* [nested Dockerfiles](#nested-dockerfiles)
* [multiple targets per Dockerfile](#multiple-targets-per-dockerfile)

Env launcher itself (`pytest_launcher`) decorates `pytest` and `ptw` tools with single interface (see [dev/start-tests](#devstart-tests-start-unitacceptance-tests), checkout `dev/start-tests --launcher-help`).


## Testing Concepts

Application written with TDD approach: tests goes ahead of code.

Most test's mindset is more **"acceptance"** rather "unit". Purpose of every test is the "feature coverage" rather than "code coverage". Every test was appeared on purpose to define the next step **over existing features**. This way it may feel like "integration fashion" and lack of mocks. It's intended choise with it's own benefits and trade-offs.

Library-level features tested in more "unit" fashion.
Core client-level features which appeared before cli was operational tested in "acceptance" fashion under `tests/` scope.
Once cli become operational next features was implemented by the coverage of integration+acceptance tests under `tests_integration/` scope.

`tests_integration/` provides multiple environments and contexts for the tests. Despite all tests written with `pytest` most of them invokes cli executable and assert stdout/stderr.

Most suites, including `tests_integration/` reuses the testing dataset defined by `tests/bt_windows/shared_fixtures.py`


## Application Concept

Main concern is to allow and help to the user to make bluetooth devices working both for Windows and Linux **with minimal steps and parameters**.

Despite existing tools, this application doesn't require 3 reboots and knowlage about windows registry, linux bluetooth configuration files and so on. Ideally application should go with minimal arguments from user. Ideally `bt-dualboot --sync-all` should be enough to do all user needs, including finding windows partition.

At the same time advanced users should be able to operate with details.


## Application Design

In order to sync bluetooth pairing keys from Linux to Windows application should:

* `bt_dualboot.windows_registry`: be able read/write windows registry hive file (candidate to be decoupled into separate package)
* `bt_dualboot.bt_windows`: represent data from windows registry as `BluetoothDevice`
* `bt_dualboot.bt_linux`: be able read and represet bluetooth devices configuration from linux
* `bt_dualboot.bt_sync_manager`: orchestrate data and processes
* (sugar) `bt_dualboot.win_mount`: be able locate mounted windows partition

By design the same core should be reused by:

* console application: `cli` module
* UI application [NOT IMPLEMENTED]
* service worker [NOT IMPLEMENTED, may be acheived by `bt-dualboot --sync-all` feature]

Additional concerns:

* Windows registry Hive-file should be updated in risk-less way (rewrite existing data without filesize change).
* Prior write operations to Hive-file backup should be created.
* User should be aware about backup location and risks of leaking backup files.
* User should have ability to preview (`--dry-run`) pending changes. Output should reflect real invokation as much as possible.


## Distribution Concept

Application should be installable with all dependencies in the familar for the regular Linux user way. Ideally user should be able install application from OS software repository. Alternatively user may download `.deb` or `.rpm` package.

As workaround user may use pypi repository. But requirement to invoke application with `sudo` forces install it with `sudo pip install` which is not recommended.


## `dev/` toolchain

`dev/` directory contains set of tools to build and use development environment


### `dev/bootstrap`: initial setup

Initial setup for development.

It's abstraction and interface point which should be used in scripts.


### `dev/start-tests`: start unit/acceptance tests

Start tests from `tests/` directory. Accepts `pytest` / `ptw` and custom arguments.

Examples:

```console
$ dev/start-tests --launcher-help
$ dev/start-tests -w                 # watch file changes: implies `ptw` instead `pytest`
$ dev/start-tests -w --pdb -x        # watch; drop into debugger on error; skip tests after error
$ dev/start-tests --shell            # spawn shell after tests for Docker context
...
```

`dev/start-tests` using `pytest_launcher` tool (see `dev/helpers.sh`)


### `dev/start-tests-integration`: integration tests for multiple environments

Prepare envoronment and start tests from for each defined environment.

**"Environment definiton"** is any directory containing executable `tests_integration/**/env_*/start`. Such executable called **"env launcher"**. Checkout `tests_integration/cli/env_single_windows/start` as example. Typically it's similar to `dev/start-tests` using `pytest_launcher`, but it is not mandatory. Env launcher may be even binary executable.

If environment directory contains `Dockerfile`, image will be built and container started with env launcher as entrypoint. Otherwise env launcher will be invoked locally.


#### invoke single environment

In scope of coding useful to invoke only subject environment. Use `ONLY_ENV=<env name>`:

```console
$ ONLY_ENV=env_single_windows dev/start-tests-integration
$ ONLY_ENV=env_single_windows dev/start-tests-integration -w
$ ONLY_ENV=env_single_windows dev/start-tests-integration --snapshot-update     # see pytest-snapshot module
...
```


#### multiple Dockerfiles (contexts) per environment

Environment may contain multiple `Dockerfile`s. Convention is

```
Dockerfile          # default context
Dockerfile.ubuntu   # additional context
Dockerfile.arch     # additional context
...
```

**Additional contexts** may be used to invoke the same set of test examples in a different context like different OS or different ways to install package. Typically bind mounts doesn't used for additional context.

**Default context** should be optimized for development process. It better bind-mount sources into container to allow `-w` watch on files changes, write-back test snapshots from container to host and so on.

Every context may be configured by creating `opts-Dockerfile*` file.
For example,

```
Dockerfile      # will be built and run with opts-Dockerfile options if exists
Dockerfile.foo  # will be built and run with opts-Dockerfile.foo options if exists
```

`opts-Dockerfile.foo` is a shell sourcable file which may looks like:

```sh
flags="pre-release"           # tags list for launcher filter (see below)
run_opts="--workdir /prj"     # append `docker run` arguments
build_opts="..."              # [NOT IMPLEMENTED, RESERVED] append `docker build` arguments
```

By default context with non-empty flags is skipped. Use `--flags` option to select additional contexts for invocation. This tool calculates intersection between `opts-Dockerfile:flags="foo bar"` and `--flags bar baz` lists and selects any context having non-empty intersection.

Special flag `no-default` allows skip default `Dockerfile`.

For example:

```console
$ dev/start-tests-integration --flags pre-release             # will select Dockerfile.foo context for invocation
$ dev/start-tests-integration --flags pre-release no-default  # will skip default Dockerfile
```

Flag `pre-release` is reserved and used by `dev/pre-release-all` tool (see below).


#### nested Dockerfiles

When common setup should be shared between few images:

```
Dockerfile
Dockerfile.foo
```

It is possible to define parent `Dockerfile.my_base` and setup both child containers with `opts-Dockerfile*` like:

```sh
require_image="my_base"
```

In this case `my_base` image will be built before building target image. `ARG_REQUIRED_IMAGE` will be passed to `docker build ...`. This way `Dockerfile` and `Dockerfile.foo` may looks like:

```Dockerfile
ARG ARG_REQUIRED_IMAGE
FROM $ARG_REQUIRED_IMAGE

RUN ...
```

In order to avoid `Dockerfile.my_base` to be built as standalone image we have to assign some flag which will never be requested. `abstract` flag is reserved for this purposes.

```sh
flags="abstract"
```

NOTE: current implementation doesn't support chain of nested containers. It will be appeared in next versions.


### multiple targets per Dockerfile

TODO


#### Tests scope

If env launcher using `pytest_launcher` then `--test-dir` is locked in the current environment only. Checkout:

```console
$ tests_integration/cli/env_single_windows/start --launcher-help
...
--tests-dir   [default: launcher dir, current='tests_integration/cli/env_single_windows/'] path to tests
...
```

Non-standard env launcher should carry proper tests scope. It's expected to invoke only tests within environment directory.


### `dev/start-tests-all`: invoke unit/acceptance and integartion tests

It's shortcut for `dev/start-tests` and `dev/start-tests-integartion` tools.


### `dev/start-tests-manual`: spawn a shell in an environment context for manual testing

Allows reuse testing environments and tests setup scenarious spawning shell inside Docker container in middle of setup and teardown steps.

See content of `dev/start-tests-manual` for details.

It uses separate pytest configuration defining as a tests target a methods named like `def manual_test_*`.

Example

```python
def manual_test_initial(debug_shell):
    """
    Spawn shell in context with having prepared Linux & Windows bluetooth configs
    invoke using:
        pytest -c manual_pytest.ini
    """
    with debug_shell():
        print("It's initial state with prepared Linux & Windows bluetooth configs")
        print(f"Command-line tip:\n  sudo ./bt-dualboot {' '.join(with_win([]))} ...")
```

`manual_test_*` willn't be invoked during regular tests run.


### `dev/pre-release-all`: ensure current working copy ready to release

* looking for DEBUG, TODO and other testing keywords
* dry-run lint
* invoke all tests including `--flags pre-release`


### `dev/pre-release/lint-all`: 

Invoke dry-run lints


### `dev/pre-release/lint-*`: 

Current approach is lint code:

1. by `black` first (see `dev/pre-release/lint-black`)
2. by `autopep8` with custom setup at second (see `dev/pre-release/lint-autopep8`)
3. check `flake8` errors and warnings (see `dev/pre-release/lint-flake8`)


## Publish to pypi repository

Building and publishing application package handled completely by poetry. This way main concern is to maintain `pyproject.toml`.

```console
$ poetry publish
```

### TIPS for staging pypi repository

```console
$ poetry config --unset repositories.local && poetry config repositories.local http://localhost:3141/user/private
$ poetry publish -r local -u user -p userpass
```

## TIPS

```
DEBUG=1 ./bt-dualboot         # force print verbose messages and artefacts
sudo DEBUG=1 ./bt-dualboot    
```
