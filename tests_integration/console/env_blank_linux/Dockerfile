ARG ARG_PYTHON_VERSION
FROM python:$ARG_PYTHON_VERSION

ARG ARG_USER ARG_UID
RUN apt update && apt install sudo \
  && useradd -m --uid "$ARG_UID" "$ARG_USER" \
  && echo "$ARG_USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$ARG_USER \
  && chmod 0440 /etc/sudoers.d/$ARG_USER

USER $ARG_USER

# pre-build dependencies
COPY ./bin/bootstrap ./requirements.txt   /tmp/prebuild/
RUN sudo chown -R $ARG_USER /tmp/prebuild \
  && cd /tmp/prebuild && ./bootstrap \
  && rm -r /tmp/prebuild
