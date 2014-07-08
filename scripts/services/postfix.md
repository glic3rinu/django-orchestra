apt-get install postfix


# http://www.postfix.org/VIRTUAL_README.html#virtual_mailbox
# https://help.ubuntu.com/community/PostfixVirtualMailBoxClamSmtpHowto
# http://wiki2.dovecot.org/HowTo/VirtualUserFlatFilesPostfix
# http://www.mailscanner.info/ubuntu.html



apt-get install dovecot-core dovecot-imapd dovecot-pop3d dovecot-lmtpd dovecot-sieve


cat > /etc/apt/sources.list.d/mailscanner.list << 'EOF'
deb http://apt.baruwa.org/debian wheezy main
deb-src http://apt.baruwa.org/debian wheezy main
EOF

wget -O - http://apt.baruwa.org/baruwa-apt-keys.gpg | apt-key add -


apt-get update
apt-get install mailscanner
