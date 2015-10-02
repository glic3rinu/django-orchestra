#!/bin/bash

set -ue


# bash <( curl https://raw.githubusercontent.com/glic3rinu/django-orchestra/master/scripts/containers/deploy.sh ) [--noinput username]

function main () {
    noinput=''
    user=$USER
    if [[ $# -eq 2 ]]; then
        if [[ $1 != '--noinput' ]]; then
            echo -e "\nErr. What argument is $1?\n" >&2
            exit 2
        elif ! id $2; then
            echo -e "\nErr. User $2 does not exist\n" >&2
            exit 3
        fi
        [ $(whoami) != 'root' ] && {
            echo -e "\nErr. --noinput should run as root\n" >&2
            exit 1
        }
        noinput='--noinput'
        run () { echo " ${bold}\$ ${@}${normal}"; ${@}; }
        surun () { echo " ${bold}\$ su $user -c \"${@}\"${normal}"; su $user -c "${@}"; }
        user=$2
    elif [[ $# -eq 1 ]]; then
        if [[ $1 != '--noinput' ]]; then
            echo -e "\nErr. What argument is $1?\n" >&2
        else
            echo -e "\nErr. --noinput should provide a username\n" >&2
        fi
        exit 1
    else
        [ $(whoami) == 'root' ] && {
            echo -e "\nErr. This script should run as a regular user\n" >&2
            exit 1
        }
        run () { echo " ${bold}\$ ${@}${normal}"; ${@}; }
        surun () { echo " ${bold}\$ ${@}${normal}"; ${@}; }
        # Test sudo privileges
        sudo true
    fi
    
    bold=$(tput -T ${TERM:-xterm} bold)
    normal=$(tput -T ${TERM:-xterm} sgr0)
    
    project_name="panel"
    if [[ $noinput == '' ]]; then
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
    
    task=cronbeat
    if [[ $noinput == '' ]]; then
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
    
    run sudo pip3 install django-orchestra==dev \
        --allow-external django-orchestra \
        --allow-unverified django-orchestra
    run sudo orchestra-admin install_requirements
    cd $(eval echo ~$user)

    surun "orchestra-admin startproject $project_name"
    cd $project_name
    
    run sudo service postgresql start
    if [[ $noinput == '--noinput' ]]; then
        db_password=$(ps aux | sha256sum | base64 | head -c 10)
        run sudo python3 -W ignore manage.py setuppostgres --noinput --db_password $db_password
    else
        run sudo python3 -W ignore manage.py setuppostgres
    fi
    surun "python3 -W ignore manage.py migrate $noinput"
    if [[ $noinput == '--noinput' ]]; then
        # Create orchestra superuser
        cat <<- EOF | surun "python3 -W ignore manage.py shell"
from orchestra.contrib.accounts.models import Account
if not Account.objects.filter(username="$user").exists():
    print('Creating orchestra superuser')
    Account.objects.create_superuser("$user", "$user@localhost", "orchestra")

EOF
    fi
    
    if [[ "$task" == "celery" ]]; then
        run sudo apt-get install rabbitmq-server
        run sudo python3 -W ignore manage.py setupcelery --username $user
    else
        surun "python3 -W ignore manage.py setupcronbeat"
        surun "python3 -W ignore manage.py syncperiodictasks"
    fi

    run sudo python3 -W ignore manage.py setuplog --noinput

    surun "python3 -W ignore manage.py collectstatic --noinput"
    run sudo apt-get install nginx-full uwsgi uwsgi-plugin-python3
    run sudo python3 -W ignore manage.py setupnginx --user $user $noinput
    run sudo python3 -W ignore manage.py restartservices
    run sudo python3 -W ignore manage.py startservices
    surun "python3 -W ignore manage.py check --deploy"
    
    # Test if serving requests
    ip_addr=$(ip addr show eth0 | grep 'inet ' | sed -r "s/.*inet ([^\s]*).*/\1/" | cut -d'/' -f1)
    if [[ $ip_addr == '' ]]; then
        ip_addr=127.0.0.1
    fi
    echo
    echo ${bold}
    echo "> Checking if Orchestra is serving on https://${ip_addr}/admin/ ..."
    if [[ $noinput == '--noinput' ]]; then
        echo -e "  - username: $user"
        echo -e "  - password: orchestra"
    fi
    
    if [[ $(curl -L -k -v -c /tmp/cookies.txt -b /tmp/cookies.txt https://$ip_addr/admin/ | grep 'Panel Hosting Management') ]]; then
        token=$(grep csrftoken /tmp/cookies.txt | awk {'print $7'})
        if [[ $(curl -L -k -v -c /tmp/cookies.txt -b /tmp/cookies.txt \
            -d "username=$user&password=orchestra&csrfmiddlewaretoken=$token" \
            -e https://$ip_addr/admin/ \
            https://$ip_addr/admin/login/?next=/admin/ | grep '<title>Panel Hosting Management</title>') ]]; then
                echo "  ** Orchestra appears to be working!"
        else
            echo "  ** Err. Couldn't login :(" >&2
        fi
    else
        echo "  ** Err. Orchestra is not responding responding on https://${ip_addr}/admin/" >&2
    fi
    echo ${normal}
}

# Wrap it all on a function to avoid partial executions when running through wget/curl
main $@
