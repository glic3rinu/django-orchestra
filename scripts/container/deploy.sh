#!/bin/bash

# Automated development deployment of django-orchestra

# This script is safe to run several times, for example in order to upgrade your deployment


set -u
bold=$(tput bold)
normal=$(tput sgr0)


[ $(whoami) != 'root' ] && {
    echo -e "\nErr. This script should run as root\n" >&2
    exit 1
}

USER='orchestra'
PASSWORD="orchestra"
HOME="/home/$USER"
PROJECT_NAME='panel'
BASE_DIR="$HOME/$PROJECT_NAME"


run () {
    echo " ${bold}\$ su $USER -c \"${@}\"${normal}"
    su $USER -c "${@}"
}


# Create a system user for running Orchestra
useradd orchestra -s "/bin/bash"
echo "$USER:$PASSWORD" | chpasswd
mkdir $HOME
chown $USER.$USER $HOME
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
    run "orchestra-admin startproject $PROJECT_NAME"
    cd -
fi

MANAGE="$BASE_DIR/manage.py"

if [[ ! $(sudo su postgres -c "psql -lqt" | awk {'print $1'} | grep '^orchestra$') ]]; then
    # orchestra database does not esists
    # Speeding up tests, don't do this in production!
    POSTGRES_VERSION=$(psql --version | head -n1 | awk {'print $3'} | cut -d'.' -f1,2)
    sudo sed -i "s/^#fsync =\s*.*/fsync = off/" \
            /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf
    sudo sed -i "s/^#full_page_writes =\s*.*/full_page_writes = off/" \
            /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf
    
    sudo service postgresql restart
    sudo python $MANAGE setuppostgres --db_name orchestra --db_user orchestra --db_password orchestra
    # Create database permissions are needed for running tests
    sudo su postgres -c 'psql -c "ALTER USER orchestra CREATEDB;"'
fi

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
from orchestra.apps.accounts.models import Account
if not User.objects.filter(username=$USER).exists():
    print 'Creating orchestra superuser'
    user = User.objects.create_superuser($USER, "'$USER@localhost'", $PASSWORD)
    user.account = Account.objects.create(user=user)
    user.save()

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
