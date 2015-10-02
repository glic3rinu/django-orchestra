FROM debian:latest

RUN apt-get -y update && apt-get install -y \
    git \
    screen \
    sudo \
    python3 \
    python3-pip \
    wget \
    curl \
    dnsutils \
    rsyslog \
    nano \
    ssh-client \
    python3-psycopg2 \
    postgresql \
    nginx-full \
    uwsgi \
    uwsgi-plugin-python3

RUN export TERM=xterm; curl https://raw.githubusercontent.com/glic3rinu/django-orchestra/master/orchestra/bin/orchestra-admin | bash -s install_requirements

RUN apt-get clean

RUN useradd orchestra --shell /bin/bash && \
    { echo "orchestra:orchestra" | chpasswd; } && \
    mkhomedir_helper orchestra && \
    adduser orchestra sudo
