ARG ARG_PYTHON_VERSION
FROM python:$ARG_PYTHON_VERSION

ARG ARG_USER ARG_UID
RUN apt update && apt install sudo \
  && useradd -m --uid "$ARG_UID" "$ARG_USER" \
  && echo "$ARG_USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$ARG_USER \
  && chmod 0440 /etc/sudoers.d/$ARG_USER \
  && apt install chntpw

COPY ./tests/bt_linux/data_samples/bt_sample_01/          /var/lib/bluetooth/
COPY ./tests/windows_registry/data_samples/SYSTEM_BLANK   /mnt/win/Windows/System32/config/SYSTEM
COPY ./bin/bootstrap ./requirements.txt                   /tmp/prebuild/

USER $ARG_USER
RUN echo 'PATH=/usr/sbin:$PATH' > /home/$ARG_USER/.bashrc \
  && sudo chmod -R uo+rw /mnt/win/Windows/System32/config \
  && sudo chown -R $ARG_USER /tmp/prebuild \
  && cd /tmp/prebuild && ./bootstrap \
  && rm -r /tmp/prebuild
