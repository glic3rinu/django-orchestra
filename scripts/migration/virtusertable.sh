#!/bin/bash


VIRTUALTABLE="/etc/postfix/virtusertable"


echo "from orchestra.apps.users import User"
echo "from orchestra.apps.users.roles.mailbox import Address, Mailbox"
echo "from orchestra.apps.domains import Domain"

cat "$VIRTUALTABLE"|grep -v "^\s*$"|while read line; do
    NAME=$(echo "$line" | awk {'print $1'} | cut -d'@' -f1)
    DOMAIN=$(echo "$line" | awk {'print $1'} | cut -d'@' -f2)
    DESTINATION=$(echo "$line" | awk '{$1=""; print $0}' | sed -e 's/^ *//' -e 's/ *$//')
    echo "domain = Domain.objects.get(name='$DOMAIN')"
    for PLACE in $DESTINATION; do
        if [[ ! $(echo $PLACE | grep '@') ]]; then
            echo "try:"
            echo "    user = User.objects.get(username='$PLACE')"
            echo "except:"
            echo "    print 'User $PLACE does not exists'"
            echo "else:"
            echo "    mailbox, __ = Mailbox.objects.get_or_create(user=user)"
            echo "    if user.account_id != 1:"
            echo "        user.account=domain.account"
            echo "        user.save()"
            echo ""
        fi
    done
    echo "address, __ = Address.objects.get_or_create(name='$NAME', domain=domain)"
    echo "address.account=domain.account"
    echo "address.destination='$DESTINATION'"
    echo "address.save()"
done
