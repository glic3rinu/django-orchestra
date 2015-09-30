FROM debian:latest

RUN apt-get -y update && apt-get install -y git screen sudo python3 python3-pip wget curl dnsutils rsyslog nano ssh-client

RUN curl https://raw.githubusercontent.com/glic3rinu/django-orchestra/master/orchestra/bin/orchestra-admin | bash -s install_requirements

RUN apt-get -y install python3-psycopg2 postgresql nginx-full uwsgi uwsgi-plugin-python3
RUN apt-get clean

RUN useradd orchestra --password 'orchestra' && \
    mkdir /home/orchestra && \
    chmod 750 /home/orchestra && \
    chown orchestra:orchestra /home/orchestra && \
    adduser orchestra sudo
