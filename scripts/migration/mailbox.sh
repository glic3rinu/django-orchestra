#!/bin/bash

# This script assumes accounts.sh has already been executed

echo "from orchestra.apps.users.models import User"
echo "from orchestra.apps.users.models.roles.mailbox import Mailbox"

SHADOW="/var/yp/ypfiles/shadow"
BASE_ACCOUNT=1

cat $SHADOW | while read line; do
    USERNAME=$(echo "$line" | cut -d':' -f1)
    PASSWORD=$(echo "$line" | cut -d':' -f2)
    echo "try:"
    echo "    user = User.objects.get(username='$USERNAME')"
    echo "except:"
    echo "    user = User.objects.create(username='$USERNAME', password='$PASSWORD', account_id=$BASE_ACCOUNT)"
    echo "    Mailbox.objects.create(user=user)"
    echo ""
    
    UNDERSCORED_ACCOUNT_NAME=${USERNAME//*_/}
    DOTTED_ACCOUNT_NAME=${USERNAME//*./}
    echo "if user.account_id == $BASE_ACCOUNT:"
    echo "    try:"
    echo "        account = User.objects.get(username='$UNDERSCORED_ACCOUNT_NAME').account"
    echo "        user.account = account"
    echo "        user.save()"
    echo "    except:"
    echo "        try:"
    echo "            account = User.objects.get(username='$DOTTED_ACCOUNT_NAME').account"
    echo "            user.account = account"
    echo "            user.save()"
    echo "        except:"
    echo "            pass"
    echo ""
done
