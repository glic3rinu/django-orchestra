#!/bin/bash

# GENERATES Python code that will fill your Orchestra database with the existing zone files
#
# DEPENDS on bind9utils
#    sudo apt-get install bind9utils
#
# EXAMPLE
#   1) bash bind9-domains.sh /etc/bind/master > bind9-domains.migrate.py
#   2) python manage.py shell < bind9-domains9.migrate.py


ZONE_PATH=${1:-/etc/bind/master/}

echo "from orchestra.apps.domains.models import Domain"
echo "from orchestra.apps.accounts.models import Account"

echo "account = Account.objects.get(pk=1)"
ERRORS=""
while read name; do
    [[ -f $name ]] && {
        [[ ! $(echo "$name" | grep '/' > /dev/null ) ]] && name="./${name}"
        ZONE_PATH=${name%/*}
        name=${name##*/}
    }
    ZONE=$(named-checkzone -D $name ${ZONE_PATH}/$name)
    if [[ $? != 0 ]]; then
        ERRORS="${ERRORS} $name"
    else
        for DOMAIN in $(echo "$ZONE" | awk {'print $1'} | uniq); do
            echo "try:"
            echo "    domain = Domain.objects.get(name='${DOMAIN%?}')"
            echo "except:"
            echo "    domain = Domain.objects.create(name='${DOMAIN%?}', account=account)"
            echo ""
            RECORDS=$(echo "$ZONE" | grep '\sIN\s' | grep "^${DOMAIN}\s")
            echo "$RECORDS" | while read record; do
                TYPE=$(echo "$record" | awk {'print $4'})
                VALUE=$(echo "$record" | sed "s/.*IN\s[A-Z]*\s*//")
                # WARNING This is example code for exclude default records !!
                if [[
                    ! ( $TYPE == 'SOA' ) &&
                    ! ( $TYPE == 'MX' && $(echo $VALUE | grep 'pangea.org') ) &&
                    ! ( $TYPE == 'A' && $VALUE == '77.246.179.81' ) &&
                    ! ( $TYPE == 'CNAME' && $VALUE = 'web.pangea.org.' ) &&
                    ! ( $TYPE == 'NS' && $(echo $VALUE | grep 'pangea.org') )
                ]]; then
                    echo "domain.records.get_or_create(type='$TYPE', value='$VALUE')"
                fi
            done
        done
    fi
done < <(ls $ZONE_PATH)

[[ $ERRORS != "" ]] && echo "Not included due to errors:$ERRORS" >& 2
