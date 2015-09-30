FROM debian:latest
RUN apt-get -y update && apt-get install -y git screen sudo python3 python3-pip wget curl dnsutils rsyslog nano ssh-client
RUN export TERM=xterm; curl https://raw.githubusercontent.com/glic3rinu/django-orchestra/master/orchestra/bin/orchestra-admin | bash -s install_requirements
RUN apt-get clean
