
echo "from orchestra.apps.accounts.models import Account"
echo "from orchestra.apps.users.models import User"

cd /etc/apache2/sites-enabled/
ls | while read line; do
    USERNAME=$(echo $line|sed "s/\.conf//")
    SHADOW=$(grep "^$USERNAME:" /var/yp/ypfiles/shadow)
    [[ $SHADOW ]] && {
        echo "user,__ = User.objects.get_or_create(username='$USERNAME')"
        echo "account, __ = Account.objects.get_or_create(user=user)"
        echo "user.password = '$(echo $SHADOW|cut -d: -f2)'"
        echo "user.account = account"
        echo "user.save()"
   }
done
cd - &> /dev/null
