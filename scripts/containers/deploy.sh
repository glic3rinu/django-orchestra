#!/bin/bash

set -ue


# bash <( curl https://raw.githubusercontent.com/glic3rinu/django-orchestra/master/scripts/containers/deploy.sh )

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
    
    # Test sudo privileges
    sudo true
    
    while true; do
        read -p "Enter a project name [panel]: " project_name
        if [[ "$project_name" == "" ]]; then
            project_name="panel"
            break
        elif [[ ! $(echo "$project_name" | grep '^[_a-zA-Z]\w*$') ]]; then
            if [[ ! $(echo "$project_name" | grep '^[_a-zA-Z]') ]]; then
                message='make sure the name begins with a letter or underscore'
            else
                message='use only numbers, letters and underscores'
            fi
            echo "'$project_name' is not a valid %s name. Please $message."
        else
            break
       fi
    done
    
    # TODO detect if already installed and don't ask stupid question
    
    while true; do
        read -p "Do you want to use celery or cronbeat (orchestra.contrib.tasks) for task execution [cronbeat]? " task
        case $task in
            'celery' ) task=celery; break;;
            'cronbeat' ) task=orchestra.contrib.tasks; break;;
            '' ) task=orchestra.contrib.tasks; break;;
            * ) echo "Please answer celery or cronbeat.";;
        esac
    done

    run sudo pip3 install django-orchestra==dev \
        --allow-external django-orchestra \
        --allow-unverified django-orchestra
    run sudo orchestra-admin install_requirements
    run cd $(eval echo ~$USER)

    run orchestra-admin startproject $project_name
    run cd $project_name
    
    sudo service postgresql start
    run sudo python3 -W ignore manage.py setuppostgres

    run python3 -W ignore manage.py migrate

    if [[ "$task" == "celery" ]]; then
        run sudo apt-get install rabbitmq-server
        run sudo python3 -W ignore manage.py setupcelery --username $USER
    else
        run python3 -W ignore manage.py setupcronbeat
        run python3 -W ignore manage.py syncperiodictasks
    fi

    run sudo python3 -W ignore manage.py setuplog --noinput

    run python3 -W ignore manage.py collectstatic --noinput
    run sudo apt-get install nginx-full uwsgi uwsgi-plugin-python3
    run sudo python3 -W ignore manage.py setupnginx --user $USER
    run sudo python3 -W ignore manage.py restartservices
    run sudo python3 -W ignore manage.py startservices
    run python3 -W ignore manage.py check --deploy
    
    ip_addr=$(ip addr show eth0 | grep 'inet ' | sed -r "s/.*inet ([^\s]*).*/\1/" | cut -d'/' -f1)
    if [[ $ip_addr == '' ]]; then
        ip_addr=127.0.0.1
    fi
    echo
    echo -e "${bold}Checking if Orchestra is working at https://${ip_addr}/admin/${normal} ...\n"
    if [[ $(curl https://$ip_addr/admin/ -I -k -s | grep 'HTTP/1.1 302 FOUND') ]]; then
        echo -e "${bold}Orchestra appears to be working!\n"
    else
        echo -e "${bold}Err. Orchestra is not responding responding at https://${ip_addr}/admin/${normal}\n" >&2
    fi
}

# Wrap it all on a function to avoid partial executions when running through wget/curl
main
