#!/bin/bash

# Automated development deployment of django-orchestra

set -u
bold=$(tput bold)
normal=$(tput sgr0)


[ $(whoami) != 'root' ] && {
    echo -e "\nErr. This script should run as root\n" >&2
    exit 1
}

USER='orchestra'
BASE_DIR='/home/orchestra/panel'
MANAGE="$BASE_DIR/panel/manage.py"

run () {
    echo " ${bold}\$ su $USER -c \"${@}\"${normal}"
    su $USER -c "${@}"
}


sudo adduser $USER sudo

CURRENT_VERSION=$(python -c "from orchestra import get_version; print get_version();" || echo false)

if [[ ! $CURRENT_VERSION ]]; then
    # First Orchestra installation
    run git clone https://github.com/glic3rinu/django-orchestra.git ~/django-orchestra
    echo ~/django-orchestra/ | sudo tee /usr/local/lib/python2.7/dist-packages/orchestra.pth
    sudo cp ~orchestra/django-orchestra/orchestra/bin/orchestra-admin /usr/local/
    sudo orchestra-admin install_requirements
fi

if [[ ! -e $BASE_DIR ]]; then
    run orchestra-admin clone $BASE_DIR
fi

sudo service postgresql start
sudo python MANAGE setuppostgres --db_name orchestra --db_user orchestra --db_password orchestra

if [[ $CURRENT_VERSION != false ]]; then
    # Per version upgrade specific operations
    sudo python MANAGE postupgradeorchestra --no-restart --from $CURRENT_VERSION
else
    sudo python MANAGE syncdb --noinput
    sudo python MANAGE migrate --noinput
fi

sudo python MANAGE setupcelery --username $USER --processes 2

# Install and configure Nginx web server
run mkdir -p $BASE_DIR/static
run python MANAGE collectstatic --noinput
sudo apt-get install -y nginx uwsgi uwsgi-plugin-python
sudo python manage.py setupnginx

# Apply changes
sudo python MANAGE restartservices

# Create a orchestra user
cat <<- EOF | python MANAGE shell
	from users.models import *
	if not User.objects.filter(username='orchestra').exists():
	    print 'Creating orchestra superuser'
	    User.objects.create_superuser('orchestra', 'orchestra@localhost', 'orchestra')
	
EOF
