FROM debian:latest

RUN apt-get -y update && apt-get install -y curl sudo

RUN export TERM=xterm; curl -L http://git.io/orchestra-admin | bash -s install_requirements

RUN apt-get clean

RUN useradd orchestra --shell /bin/bash && \
    { echo "orchestra:orchestra" | chpasswd; } && \
    mkhomedir_helper orchestra && \
    adduser orchestra sudo
