apt-get install mailman

newlist mailman


echo 'mailman:              "|/var/lib/mailman/mail/mailman post mailman"
mailman-admin:        "|/var/lib/mailman/mail/mailman admin mailman"
mailman-bounces:      "|/var/lib/mailman/mail/mailman bounces mailman"
mailman-confirm:      "|/var/lib/mailman/mail/mailman confirm mailman"
mailman-join:         "|/var/lib/mailman/mail/mailman join mailman"
mailman-leave:        "|/var/lib/mailman/mail/mailman leave mailman"
mailman-owner:        "|/var/lib/mailman/mail/mailman owner mailman"
mailman-request:      "|/var/lib/mailman/mail/mailman request mailman"
mailman-subscribe:    "|/var/lib/mailman/mail/mailman subscribe mailman"
mailman-unsubscribe:  "|/var/lib/mailman/mail/mailman unsubscribe mailman"' >> /etc/aliases


postalias /etc/aliases


/etc/init.d/mailman start




# postifx

relay_domains = $mydestination, lists.orchestra.lan
relay_recipient_maps = hash:/var/lib/mailman/data/aliases
transport_maps = hash:/etc/postfix/transport
mailman_destination_recipient_limit = 1



echo "lists.orchestra.lan   mailman:" >> /etc/postfix/transport

postmap /etc/postfix/transport

echo 'MTA = "Postfix"
POSTFIX_STYLE_VIRTUAL_DOMAINS = ["lists.orchestra.lan"]
# alias for postmaster, abuse and mailer-daemon
DEB_LISTMASTER = "postmaster@orchestra.lan"' >> /etc/mailman/mm_cfg.py


sed -i "s/DEFAULT_EMAIL_HOST\s*=\s*.*/DEFAULT_EMAIL_HOST = 'lists.orchestra.lan'/" /etc/mailman/mm_cfg.py
sed -i "s/DEFAULT_URL_HOST\s*=\s*.*/DEFAULT_URL_HOST   = 'lists.orchestra.lan'/" /etc/mailman/mm_cfg.py


# apache
cp /etc/mailman/apache.conf /etc/apache2/sites-available/mailman.conf
a2ensite mailman.conf
/etc/init.d/apache2 restart


