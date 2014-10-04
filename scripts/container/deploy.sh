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
PASSWORD='orchestra'
HOME="/home/$USER"
PROJECT_NAME='panel'
BASE_DIR="$HOME/$PROJECT_NAME"


surun () {
    echo " ${bold}\$ su $USER -c \"${@}\"${normal}"
    su $USER -c "${@}"
}

run () {
    echo " ${bold}\$ ${@}${normal}"
    ${@}
}


# Create a system user for running Orchestra
useradd orchestra -s "/bin/bash"
echo "$USER:$PASSWORD" | chpasswd
mkdir $HOME
chown $USER.$USER $HOME
run adduser $USER sudo


CURRENT_VERSION=$(python -c "from orchestra import get_version; print get_version();" 2> /dev/null || false)

if [[ ! $CURRENT_VERSION ]]; then
    # First Orchestra installation
    run "apt-get -y install git python-pip"
    surun "git clone https://github.com/glic3rinu/django-orchestra.git ~/django-orchestra"
    echo $HOME/django-orchestra/ | sudo tee /usr/local/lib/python2.7/dist-packages/orchestra.pth
    run "cp $HOME/django-orchestra/orchestra/bin/orchestra-admin /usr/local/bin/"
fi

sudo orchestra-admin install_requirements --testing

if [[ ! -e $BASE_DIR ]]; then
    cd $HOME
    surun "orchestra-admin startproject $PROJECT_NAME"
    cd -
fi

MANAGE="$BASE_DIR/manage.py"

if [[ ! $(sudo su postgres -c "psql -lqt" | awk {'print $1'} | grep '^orchestra$') ]]; then
    # orchestra database does not esists
    # Speeding up tests, don't do this in production!
    POSTGRES_VERSION=$(psql --version | head -n1 | awk {'print $3'} | sed -r "s/(^[0-9\.]*).*/\1/")
    sed -i "s/^#fsync =\s*.*/fsync = off/" \
            /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf
    sed -i "s/^#full_page_writes =\s*.*/full_page_writes = off/" \
            /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf
    
    run "service postgresql restart"
    run "python $MANAGE setuppostgres --db_name orchestra --db_user orchestra --db_password orchestra"
    # Create database permissions are needed for running tests
    sudo su postgres -c 'psql -c "ALTER USER orchestra CREATEDB;"'
fi

if [[ $CURRENT_VERSION ]]; then
    # Per version upgrade specific operations
    run "python $MANAGE postupgradeorchestra --no-restart --from $CURRENT_VERSION"
else
    run "python $MANAGE syncdb --noinput"
    run "python $MANAGE migrate --noinput"
fi

sudo python $MANAGE setupcelery --username $USER --processes 2

# Install and configure Nginx web server
surun "mkdir $BASE_DIR/static"
surun "python $MANAGE collectstatic --noinput"
run "apt-get install -y nginx uwsgi uwsgi-plugin-python"
run "python $MANAGE setupnginx"
run "service nginx start"

# Apply changes
run "python $MANAGE restartservices"

# Create a orchestra user
cat <<- EOF | python $MANAGE shell
from orchestra.apps.accounts.models import Account
if not Account.objects.filter(username="$USER").exists():
    print 'Creating orchestra superuser'
    __ = Account.objects.create_superuser("$USER", "'$USER@localhost'", "$PASSWORD")

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
