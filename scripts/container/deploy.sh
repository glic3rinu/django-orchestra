#!/bin/bash

# Automated development deployment of django-orchestra

# This script is safe to run several times, for example in order to upgrade your deployment

# TODO speedup postgres

set -u
bold=$(tput bold)
normal=$(tput sgr0)


[ $(whoami) != 'root' ] && {
    echo -e "\nErr. This script should run as root\n" >&2
    exit 1
}

USER='orchestra'
PASSWORD="orchestra"
HOME=$(eval echo "~$USER")
PROJECT_NAME='panel'
BASE_DIR="$HOME/$PROJECT_NAME"
MANAGE="$BASE_DIR/manage.py"

run () {
    echo " ${bold}\$ su $USER -c \"${@}\"${normal}"
    su $USER -c "${@}"
}


# Create a system user for running Orchestra
useradd orchestra -s "/bin/bash"
echo "$USER:$PASSWORD" | chpasswd
mkdir /home/$USER
chown $USER.$USER /home/$USER
sudo adduser $USER sudo


CURRENT_VERSION=$(python -c "from orchestra import get_version; print get_version();" 2> /dev/null || false)

if [[ ! $CURRENT_VERSION ]]; then
    # First Orchestra installation
    run "git clone https://github.com/glic3rinu/django-orchestra.git ~/django-orchestra"
    echo $HOME/django-orchestra/ | sudo tee /usr/local/lib/python2.7/dist-packages/orchestra.pth
    sudo cp $HOME/django-orchestra/orchestra/bin/orchestra-admin /usr/local/bin/
    sudo orchestra-admin install_requirements
fi

if [[ ! -e $BASE_DIR ]]; then
    cd $HOME
    run "orchestra-admin clone $PROJECT_NAME"
    cd -
fi

sudo service postgresql start
sudo python $MANAGE setuppostgres --db_name orchestra --db_user orchestra --db_password orchestra

if [[ $CURRENT_VERSION ]]; then
    # Per version upgrade specific operations
    sudo python $MANAGE postupgradeorchestra --no-restart --from $CURRENT_VERSION
else
    sudo python $MANAGE syncdb --noinput
    sudo python $MANAGE migrate --noinput
fi

sudo python $MANAGE setupcelery --username $USER --processes 2

# Install and configure Nginx web server
run "mkdir $BASE_DIR/static"
run "python $MANAGE collectstatic --noinput"
sudo apt-get install -y nginx uwsgi uwsgi-plugin-python
sudo python $MANAGE setupnginx
sudo service nginx start

# Apply changes
sudo python $MANAGE restartservices

# Create a orchestra user
cat <<- EOF | python $MANAGE shell
from django.contrib.auth.models import User
if not User.objects.filter(username=$USER).exists():
    print 'Creating orchestra superuser'
    User.objects.create_superuser($USER, "'$USER@localhost'", $PASSWORD)

EOF

# Change to development settings
PRODUCTION="from orchestra.conf.production_settings import \*"
DEVEL="from orchestra.conf.devel_settings import \*"
sed -i "s/^$PRODUCTION/# $PRODUCTION/" $BASE_DIR/$PROJECT_NAME/settings.py
sed -i "s/^#\s*$DEVEL/$DEVEL/" $BASE_DIR/$PROJECT_NAME/settings.py


cat << EOF

${bold}
 * Admin interface login *
    - username: $USER
    - password: $PASSWORD
${normal}
EOF
