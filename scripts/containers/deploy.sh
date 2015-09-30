#!/bin/bash

# Automated development deployment of django-orchestra

# This script is safe to run several times, for example in order to upgrade your deployment

set -ue

function main () {


bold=$(tput -T ${TERM:-xterm} bold)
normal=$(tput -T ${TERM:-xterm} sgr0)

surun () {
    echo " ${bold}\$ su $USER -c \"${@}\"${normal}"
    su $USER -c "${@}"
}


run () {
    echo " ${bold}\$ ${@}${normal}"
    ${@}
}


[ $(whoami) != 'root' ] && {
    echo -e "\nErr. This script should run as root\n" >&2
    exit 1
}

USER='orchestra'
PASSWORD='orchestra'
HOME="/home/$USER"
PROJECT_NAME='panel'
BASE_DIR="$HOME/$PROJECT_NAME"
MANAGE="$BASE_DIR/manage.py"
PYTHON_BIN="python3"
CELERY=false


# Create a system user for running Orchestra
useradd $USER -s "/bin/bash" || true
echo "$USER:$PASSWORD" | chpasswd
mkdir -p $HOME
chown $USER.$USER $HOME
groups $USER | grep -E "(^|\s)$USER($|\s)" > /dev/null || run adduser $USER sudo


CURRENT_VERSION=$($PYTHON_BIN -c "from orchestra import get_version; print(get_version());" 2> /dev/null || false) || true
if [[ ! $CURRENT_VERSION ]]; then
    # First Orchestra installation
    run "apt-get -y install git python3-pip"
    surun "git clone https://github.com/glic3rinu/django-orchestra.git ~/django-orchestra" || {
        # Finishing partial installation
        surun "export GIT_DIR=~/django-orchestra/.git; git pull"
    }
    PYTHON_PATH=$($PYTHON_BIN -c "import sys; print([path for path in sys.path if path.startswith('/usr/local/lib/python')][0]);")
    echo $HOME/django-orchestra/ | sudo tee "$PYTHON_PATH/orchestra.pth"
fi

run "cp $HOME/django-orchestra/orchestra/bin/orchestra-admin /usr/local/bin/"
run "cp $HOME/django-orchestra/orchestra/bin/orchestra-beat /usr/local/bin/"

sudo orchestra-admin install_requirements --testing

if [[ ! -e $BASE_DIR ]]; then
    cd $HOME
    surun "orchestra-admin startproject $PROJECT_NAME"
    cd -
else
    echo "$BASE_DIR already existis, doing nothing."
fi


run "apt-get -y install postgresql"
if [[ ! $(sudo su postgres -c "psql -lqt" | awk {'print $1'} | grep '^orchestra$') ]]; then
    # orchestra database does not exists
    # Speeding up tests, don't do this in production!
    . /usr/share/postgresql-common/init.d-functions
    POSTGRES_VERSION=$(psql --version | head -n1 | sed -r "s/^.*\s([0-9]+\.[0-9]+).*/\1/")
    sed -i "s/^#fsync =\s*.*/fsync = off/" \
            /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf
    sed -i "s/^#full_page_writes =\s*.*/full_page_writes = off/" \
            /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf
    
    run "service postgresql restart"
    run "$PYTHON_BIN $MANAGE setuppostgres --db_name orchestra --db_user orchestra --db_password orchestra"
    # Create database permissions are needed for running tests
    sudo su postgres -c 'psql -c "ALTER USER orchestra CREATEDB;"'
fi

# create logfile
surun "$PYTHON_BIN $MANAGE setuplog --noinput"


# admin_tools needs accounts and does not have migrations
if [[ ! $(sudo su postgres -c "psql orchestra -q -c 'SELECT * FROM accounts_account LIMIT 1;' 2> /dev/null") ]]; then
    surun "$PYTHON_BIN $MANAGE migrate --noinput"
else
    surun "$PYTHON_BIN $MANAGE postupgradeorchestra --from $CURRENT_VERSION"
fi


if [[ $CELERY == true ]]; then
    run apt-get install -y rabbitmq
    sudo $PYTHON_BIN $MANAGE setupcelery --username $USER --processes 2
else
    surun "$PYTHON_BIN $MANAGE setupcronbeat"
    surun "$PYTHON_BIN $MANAGE syncperiodictasks"
fi


# Install and configure Nginx+uwsgi web services
surun "mkdir -p $BASE_DIR/static"
surun "$PYTHON_BIN $MANAGE collectstatic --noinput"
run "apt-get install -y nginx uwsgi uwsgi-plugin-python3"
run "$PYTHON_BIN $MANAGE setupnginx --user $USER --noinput"
run "service nginx start"

# Apply changes on related services
run "$PYTHON_BIN $MANAGE restartservices" || true

# Create orchestra superuser
cat <<- EOF | $PYTHON_BIN $MANAGE shell
from orchestra.contrib.accounts.models import Account
if not Account.objects.filter(username="$USER").exists():
    print('Creating orchestra superuser')
    Account.objects.create_superuser("$USER", "$USER@localhost", "$PASSWORD")

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

}

# Wrap it all on a function to avoid partial executions when running through wget/curl
main
