#!/bin/bash

set -ue

# https://git.io/deploy-orchestra
# bash <( curl https://raw.githubusercontent.com/glic3rinu/django-orchestra/master/scripts/containers/deploy.sh ) [--noinput username]


bold=$(tput -T ${TERM:-xterm} bold)
normal=$(tput -T ${TERM:-xterm} sgr0)


function test_orchestra () {
    user=$1
    ip_addr=$2
    # Test if serving requests
    echo
    echo ${bold}
    echo "> Checking if Orchestra is serving on https://${ip_addr}/admin/ ..."
    if [[ $noinput ]]; then
        echo "  - username: $user"
        echo "  - password: orchestra${normal}"
    fi
    echo
    if [[ $(curl -s -L -k -c /tmp/cookies.txt -b /tmp/cookies.txt https://$ip_addr/admin/ | grep 'Panel Hosting Management') ]]; then
        token=$(grep csrftoken /tmp/cookies.txt | awk {'print $7'})
        if [[ $(curl -s -L -k -c /tmp/cookies.txt -b /tmp/cookies.txt \
            -d "username=$user&password=orchestra&csrfmiddlewaretoken=$token" \
            -e https://$ip_addr/admin/ \
            https://$ip_addr/admin/login/?next=/admin/ | grep '<title>Panel Hosting Management</title>') ]]; then
                echo "${bold}  ** Orchestra appears to be working!${normal}"
        else
            echo "${bold}  ** Err. Couldn't login :(${normal}" >&2
        fi
    else
        echo "${bold}  ** Err. Orchestra is not responding responding on https://${ip_addr}/admin/${normal}" >&2
    fi
    echo
}


function install_orchestra () {
    dev=$1
    home=$2
    repo=$3
    
    if [[ $dev ]]; then
        # Install from source
        python_path=$(python3 -c "import sys; print([path for path in sys.path if path.startswith('/usr/local/lib/python')][0]);")
        if [[ -d $python_path/orchestra ]]; then
            run sudo rm -fr $python_path/orchestra
        fi
        orch_version=$(python3 -c "from orchestra import get_version; print(get_version());" 2> /dev/null)
        if [[ ! $orch_version ]]; then
            # First Orchestra installation
            run sudo apt-get -y install git python3-pip
            surun "git clone $repo $home/django-orchestra" || {
                # Finishing partial installation
                surun "export GIT_DIR=$home/django-orchestra/.git; git pull"
            }
            echo $home/django-orchestra/ | sudo tee "$python_path/orchestra.pth"
        else
            echo "You may want to execute 'git pull origin master'?"
        fi
        if [[ -L /usr/local/bin/orchestra-admin || -f /usr/local/bin/orchestra-admin ]]; then
            run sudo rm -f /usr/local/bin/{orchestra-admin,orchestra-beat}
        fi
        run sudo ln -s $home/django-orchestra/orchestra/bin/orchestra-admin /usr/local/bin/
        run sudo ln -s $home/django-orchestra/orchestra/bin/orchestra-beat /usr/local/bin/
        run sudo orchestra-admin install_requirements --testing
    else
        # Install from pip
        run sudo pip3 install http://git.io/django-orchestra-dev
        run sudo orchestra-admin install_requirements
    fi
}


function setup_database () {
    dev=$1
    noinput=$2
    run sudo apt-get install -y postgresql python3-psycopg2
    # Setup Database
    if [[ $dev ]]; then
        # Speeding up tests, don't do this in production!
        . /usr/share/postgresql-common/init.d-functions
        pg_version=$(psql --version | head -n1 | sed -r "s/^.*\s([0-9]+\.[0-9]+).*/\1/")
        sudo sed -i \
            -e "s/^#fsync =\s*.*/fsync = off/" \
            -e "s/^#full_page_writes =\s*.*/full_page_writes = off/" \
            /etc/postgresql/${pg_version}/main/postgresql.conf
    fi
    run sudo service postgresql start
    if [[ $noinput ]]; then
        db_password=$(ps aux | sha256sum | base64 | head -c 10)
        run sudo python3 -W ignore manage.py setuppostgres --noinput --db_password $db_password
    else
        run sudo python3 -W ignore manage.py setuppostgres
    fi
    if [[ $dev ]]; then
        # Create database permissions are needed for running tests
        sudo su postgres -c 'psql -c "ALTER USER orchestra CREATEDB;"'
    fi
    surun "python3 -W ignore manage.py migrate $noinput"
}


function create_orchestra_superuser () {
    user=$1
    email=$2
    password=$3
        cat <<- EOF | surun "python3 -W ignore manage.py shell"
			from orchestra.contrib.accounts.models import Account
			if not Account.objects.filter(username="$user").exists():
			    print('Creating orchestra superuser')
			    Account.objects.create_superuser("$user", "$email", "$password")
			
			EOF
}


print_help () {
    cat <<- EOF
		
		${bold}NAME${normal}
		    ${bold}deploy.sh${normal} - Deploy a django-orchestra project
		    
		${bold}SYNOPSIS${normal}
		    ${bold}deploy.sh${normal} [--noinput=USERNAME] [--dev] [--repo=GITREPO] [--projectname=NAME]
		    
		${bold}OPTIONS${normal}
		    ${bold}-n, --noinput=USERNAME${normal}
		            Execute the script without any user input, an existing system USERNAME is required.
		            requires the script to be executed as root user
		    
		    ${bold}-d, --dev${normal}
		            Perform a deployment suitable for development:
		                1. debug mode
		                2. dependencies for running tests
		                3. access to source code
		    
		    ${bold}-r, --repo=GITREPO${normal}
		            Chose which repo use for development deployment
		            this option requires --dev option to be selected
		            https://github.com/glic3rinu/django-orchestra.git is used by default
		    
		    ${bold}-p, --projectname=NAME${normal}
		            Specify a project name, this will be asked on interactive mode
		            and name 'panel' will be used otherwise.
		    
		    ${bold}-h, --help${normal}
		            Display this message
		    
		${bold}EXAMPLES${normal}
		    deploy.sh
		    
		    deploy.sh --dev
		    
		    deploy.sh --dev --noinput orchestra
		    
		EOF
}


function main () {
    # Input validation
    opts=$(getopt -o n:dr:h -l noinput:,dev,repo:,help -- "$@") || exit 1
    set -- $opts
    
    dev=
    noinput=
    user=$(whoami)
    repo='https://github.com/glic3rinu/django-orchestra.git'
    brepo=
    project_name="panel"
    bproject_name=
    
    while [ $# -gt 0 ]; do
        case $1 in
            -n|--noinput) user="${2:1:${#2}-2}"; noinput='--noinput'; shift ;;
            -r|--repo) repo="${2:1:${#2}-2}"; brepo=true; shift ;;
            -d|--dev) dev=true; ;;
            -p|--project_name) project_name="${2:1:${#2}-2}"; bproject_name=true; shift ;;
            -h|--help) print_help; exit 0 ;;
            (--) shift; break;;
            (-*) echo "$0: Err. - unrecognized option $1" 1>&2; exit 1;;
            (*) break;;
        esac
        shift
    done
    unset OPTIND
    unset opt
    
    if [[ ! $noinput ]]; then
        if [[ $(whoami) == 'root' ]]; then
            echo -e "\nErr. Interactive script should run as a regular user\n" >&2
            exit 2
        fi
        run () { echo " ${bold}\$ ${@}${normal}"; ${@}; }
        surun () { echo " ${bold}\$ ${@}${normal}"; ${@}; }
    else
        if [[ $(whoami) != 'root' ]]; then
            echo -e "\nErr. --noinput should run as root\n" >&2
            exit 3
        elif ! id $user &> /dev/null; then
            echo -e "\nErr. User $2 does not exist\n" >&2
            exit 4
        fi
        run () { echo " ${bold}\$ ${@}${normal}"; ${@}; }
        surun () { echo " ${bold}\$ su $user -c \"${@}\"${normal}"; su $user -c "${@}"; }
    fi
    if [[ ! $dev && $brepo ]]; then
        echo -e "\nErr. --repo only makes sense with --dev\n" >&2
        exit 5
    fi

    sudo true
    if [[ ! $noinput && ! $bproject_name ]]; then
        while true; do
            read -p "Enter a project name [panel]: " project_name
            if [[ ! "$project_name" ]]; then
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
    if [[ ! $noinput ]]; then
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
    
    home=$(eval echo ~$user)
    cd $home
    
    install_orchestra "$dev" $home $repo
    if [[ ! -e $project_name ]]; then
        surun "orchestra-admin startproject $project_name"
    else
        echo "Not deploying, $project_name already exists."
    fi
    cd $project_name
    setup_database "$dev" "$noinput"
    
    if [[ $noinput ]]; then
        create_orchestra_superuser $user $user@localhost orchestra
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
    
    
    ip_addr=$(ip addr show eth0 | grep 'inet ' | sed -r "s/.*inet ([^\s]*).*/\1/" | cut -d'/' -f1)
    if [[ ! $ip_addr ]]; then
        ip_addr=127.0.0.1
    fi
    
    # Configure settings file into debug mode
    if [[ $dev ]]; then
        sed -i \
            -e "s/^\s*#\s*'debug_toolbar',/    'debug_toolbar',/" \
            -e "s/^\s*#\s*'django_nose',/    'django_nose',/" $project_name/settings.py
        if [[ ! $(grep '^INTERNAL_IPS\s*=' $project_name/settings.py) ]]; then
            echo "INTERNAL_IPS = ('$ip_addr',)" >> $project_name/settings.py
        fi
    fi
    
    test_orchestra $user $ip_addr
}

# Wrap it all on a function to avoid partial executions when running through wget/curl
main $@
