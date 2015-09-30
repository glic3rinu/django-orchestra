#!/bin/bash

set -ue

function main () {
    bold=$(tput -T ${TERM:-xterm} bold)
    normal=$(tput -T ${TERM:-xterm} sgr0)

    [ $(whoami) == 'root' ] && {
        echo -e "\nErr. This script should run as a regular user\n" >&2
        exit 1
    }

    run () {
        echo " ${bold}\$ ${@}${normal}"
        ${@}
    }

    run sudo pip3 install django-orchestra==dev \
        --allow-external django-orchestra \
        --allow-unverified django-orchestra
    run sudo orchestra-admin install_requirements
    run cd $(eval echo ~$USER)

    while true; do
        read -p "Enter a project name: " project_name
        if [[ "$project_name" =~ ' ' ]]; then
            echo "Spaces not allowed"
        else
            run orchestra-admin startproject $project_name
            run cd $project_name
            break
       fi
    done

    read -p "Enter a new database password: " db_password
    run sudo python3 manage.py setuppostgres --db_password "$db_password"

    run python3 manage.py migrate
    run python3 panel/manage.py check --deploy

    function cronbeat () {
        run python3 manage.py setupcronbeat
        run python3 panel/manage.py syncperiodictasks
    }

    function celery () {
        run sudo apt-get install rabbitmq
        run sudo python3 manage.py setupcelery --username $USER
    }

    while true; do
        read -p "Do you want to use celery or cronbeat for task execution [cronbeat]?" task
        case $task in
            'celery' ) celery; break;;
            'cronbeat' ) cronbeat; break;;
            '' ) cronbeat; break;;
            * ) echo "Please answer celery or cronbeat.";;
        esac
    done

    run sudo python3 manage.py setuplog

    run python3 manage.py collectstatic --noinput
    run sudo apt-get install nginx-full uwsgi uwsgi-plugin-python3
    run sudo python3 manage.py setupnginx --user $USER
    run sudo python manage.py startservices
}

# Wrap it all on a function to avoid partial executions when running through wget/curl
main
