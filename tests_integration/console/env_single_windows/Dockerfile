ARG ARG_REQUIRED_IMAGE
FROM $ARG_REQUIRED_IMAGE

ARG ARG_USER

# pre-build dependencies
COPY ./bin/bootstrap ./pyproject.toml ./poetry.lock   /src/
RUN /docker/prebuild-dependencies $ARG_USER /src

