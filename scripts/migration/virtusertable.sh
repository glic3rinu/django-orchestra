#!/bin/bash


VIRTUALTABLE=${1-"/etc/postfix/virtusertable"}


echo "from orchestra.apps.accounts.models import Account"
echo "from orchestra.apps.mailboxes.models import Address, Mailbox"
echo "from orchestra.apps.domains.models import Domain"

echo "main_account = Account.objects.get(id=1)"
cat "$VIRTUALTABLE"|grep -v "^\s*$"|while read line; do
    NAME=$(echo "$line" | awk {'print $1'} | cut -d'@' -f1)
    DOMAIN=$(echo "$line" | awk {'print $1'} | cut -d'@' -f2)
    DESTINATION=$(echo "$line" | awk '{$1=""; print $0}' | sed -e 's/^ *//' -e 's/ *$//')
    echo "domain = Domain.objects.get(name='$DOMAIN')"
    echo "mailboxes = []"
    echo "account = main_account"
    NEW_DESTINATION=""
    for PLACE in $DESTINATION; do
        if [[ ! $(echo $PLACE | grep '@') ]]; then
            if [[ $(grep "^${PLACE}:" /etc/shadow) ]]; then
                PASSWORD=$(grep "^${PLACE}:" /etc/shadow | cut -d':' -f2)
                echo "if account == main_account and domain.account != main_account:"
                echo "    account = domain.account"
                echo "else:"
                echo "    try:"
                echo "        account = Account.objects.get(username='${PLACE}')"
                echo "    except:"
                echo "        pass"
                echo "mailboxes.append(('${PLACE}', '${PASSWORD}'))"
            else
                NEW_DESTINATION="${NEW_DESTINATION} ${PLACE}"
            fi
        else
            NEW_DESTINATION="${NEW_DESTINATION} ${PLACE}"
        fi
    done
    echo "for mailbox, password in mailboxes:"
    echo "    mailbox = mailbox.strip()"
    echo "    try:"
    echo "        mailbox = Mailbox.objects.get(username=mailbox)"
    echo "    except:"
    echo "        mailbox = Mailbox(username=mailbox, password=password, account=account)"
    echo "        try:"
    echo "            mailbox.full_clean()"
    echo "        except:"
    echo "            sys.stderr.write('cleaning')"
    echo "        else:"
    echo "            mailbox.save()"
    echo "    else:"
    echo "        if mailbox.account != account:"
    echo "            sys.stderr.write('%s != %s' % (mailbox.account, account))"
    echo "    if domain.account != account:"
    echo "        sys.stderr.write('%s != %s' % (domain.account, account))"
    echo "    address = Address(name='${NAME}', domain=domain, account=account, destination='${NEW_DESTINATION}')"
    echo "    try:"
    echo "        address.full_clean()"
    echo "    except:"
    echo "        sys.stderr.write('cleaning address')"
    echo "    else:"
    echo "        address.save()"
    echo "    domain = None"
done
