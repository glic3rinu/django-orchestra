#!/bin/bash

set -ue


# bash <( curl https://raw.githubusercontent.com/glic3rinu/django-orchestra/master/scripts/containers/deploy.sh ) [--noinput username]

function main () {
    run_ () {
        echo " ${bold}\$ ${@}${normal}"
        ${@}
    }
    
    surun_ () {
        echo " ${bold}\$ su $USER -c \"${@}\"${normal}"
        su $USER -c "${@}"
    }
    noinput=0
    if [[ $# -eq 3 ]]; then
        if [[ $1 != '--noinput' ]]; then
            echo "What argument is $1?" >&2
            exit 2
        elif ! id $2; then
            echo "User $2 does not exist" >&2
            exit 3
        fi
        noinput=1
        run=surun_
        sudorun=run_
    elif [[ $# -eq 2 ]]; then
        if [[ $1 != '--noinput' ]]; then
            echo "What argument is $1?" >&2
        else
            echo "--noinput should provide a username" >&2
        fi
        exit 1
    else
        [ $(whoami) == 'root' ] && {
            echo -e "\nErr. This script should run as a regular user\n" >&2
            exit 1
        }
        run=run_
        sudorun="run_ sudo"
        # Test sudo privileges
        sudo true
    fi
    
    bold=$(tput -T ${TERM:-xterm} bold)
    normal=$(tput -T ${TERM:-xterm} sgr0)

    project_name="panel"
    if [[ $noinput -eq 0 ]]; then
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
    fi
    
    # TODO detect if already installed and don't ask stupid question
    
    task=cronbeat
    if [[ $noinput -eq 0 ]]; then
        while true; do
            read -p "Do you want to use celery or cronbeat (orchestra.contrib.tasks) for task execution [cronbeat]? " task
            case $task in
                'celery' ) task=celery; break;;
                'cronbeat' ) task=cronbeat; break;;
                '' ) task=cronbeat; break;;
                * ) echo "Please answer celery or cronbeat.";;
            esac
        done
    fi

    sudorun pip3 install django-orchestra==dev \
        --allow-external django-orchestra \
        --allow-unverified django-orchestra
    sudorun orchestra-admin install_requirements
    run cd $(eval echo ~$USER)

    run orchestra-admin startproject $project_name
    run cd $project_name
    
    sudorun service postgresql start
    sudorun python3 -W ignore manage.py setuppostgres $1

    run python3 -W ignore manage.py migrate

    if [[ "$task" == "celery" ]]; then
        sudorun apt-get install rabbitmq-server
        sudorun python3 -W ignore manage.py setupcelery --username $USER
    else
        run python3 -W ignore manage.py setupcronbeat
        run python3 -W ignore manage.py syncperiodictasks
    fi

    sudorun python3 -W ignore manage.py setuplog --noinput

    run python3 -W ignore manage.py collectstatic --noinput
    sudorun apt-get install nginx-full uwsgi uwsgi-plugin-python3
    sudorun python3 -W ignore manage.py setupnginx --user $USER
    sudorun python3 -W ignore manage.py restartservices
    sudorun python3 -W ignore manage.py startservices
    run python3 -W ignore manage.py check --deploy
    
    ip_addr=$(ip addr show eth0 | grep 'inet ' | sed -r "s/.*inet ([^\s]*).*/\1/" | cut -d'/' -f1)
    if [[ $ip_addr == '' ]]; then
        ip_addr=127.0.0.1
    fi
    echo
    echo
    echo "${bold}> Checking if Orchestra is serving at https://${ip_addr}/admin/${normal} ..."
    if [[ $(curl https://$ip_addr/admin/ -I -k -s | grep 'HTTP/1.1 302 FOUND') ]]; then
        echo -e "${bold}  ** Orchestra appears to be working!${normal}\n"
    else
        echo -e "${bold}  ** Err. Orchestra is not responding responding at https://${ip_addr}/admin/${normal}\n" >&2
    fi
}

# Wrap it all on a function to avoid partial executions when running through wget/curl
main
