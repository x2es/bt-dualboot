ARG ARG_PYTHON_VERSION
FROM python:$ARG_PYTHON_VERSION

COPY ./docker /docker/
ARG ARG_UID ARG_USER
RUN /docker/add-user $ARG_UID $ARG_USER \
  && apt install chntpw

COPY ./tests/bt_linux/data_samples/bt_sample_01/          /var/lib/bluetooth/
COPY ./tests/windows_registry/data_samples/SYSTEM_BLANK   /mnt/win/Windows/System32/config/SYSTEM

USER $ARG_USER

# pre-build dependencies
COPY ./bin/bootstrap ./pyproject.toml ./poetry.lock   /src/
RUN /docker/prebuild-dependencies $ARG_USER /src \
  && echo 'PATH=/usr/sbin:$PATH' > /home/$ARG_USER/.bashrc \
  && sudo chmod -R uo+rw /mnt/win/Windows/System32/config \
  # since test app invoked with sudo we have to setup faketime for system-wide environment too
  && sudo pip install libfaketime

