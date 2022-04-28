ARG ARG_PYTHON_VERSION
FROM python:$ARG_PYTHON_VERSION

COPY ./docker /docker/
ARG ARG_UID ARG_USER
RUN /docker/add-user $ARG_UID $ARG_USER

USER $ARG_USER

# pre-build dependencies
COPY ./bin/bootstrap ./pyproject.toml ./poetry.lock   /src/
RUN /docker/prebuild-dependencies $ARG_USER /src
