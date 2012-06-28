{% load gapless %}

#!/bin/bash

USER="{{ object.fcgid.user.username }}"
GROUP="{{ object.fcgid.group.name }}"
FCGI_DIR="/home/httpd/fcgi-bin.d/php{{ object.php.version }}-${USER}-{{ object.unique_ident}}"
CGI_DIR="/home/pangea/${USER}/cgi-bin"
APACHE_FILE="/etc/apache2/sites-available/{{ object.unique_ident }}"

{% gapless %} 

# Generate the vhost config on a tmp file
echo -e "<VirtualHost {{ object.ip }}:{{ object.port }}>
    ServerName {{ object.ServerName }}

{% if object.DocumentRoot %}
    DocumentRoot {{ object.DocumentRoot }}
{% endif %}

{% if object.ServerAlias %}
    ServerAlias {{ object.ServerAlias }}
{% endif %}

{% if object.CustomLog %}
    CustomLog {{ object.CustomLog }}
{% endif %}
	
    SuexecUserGroup ${USER} ${GROUP}
    Action php-fcgi /fcgi-bin/php-fcgi-wrapper
    ScriptAlias /cgi-bin/ ${CGI_DIR}
{{ object.rendered_custom_directives }}
</VirtualHost>" > /tmp/{{ object.unique_ident }}

{% endgapless %}

# Reload apache config only if required
if [[ ! -e ${APACHE_FILE} || $(diff /tmp/{{ object.unique_ident }} ${APACHE_FILE}) ]]; then
    mv /tmp/{{ object.unique_ident }} ${APACHE_FILE}
    {% if object.active %}
        ln -s ${APACHE_FILE} /etc/apache2/sites-enabled/
        #TODO: if configtest goes wrong, send email to admin
        if [[ $(apache2ctl configtest) ]]; then
            /etc/init.d/apache2 reload
        fi
    {% else %}
        if [[ -e /etc/apache2/sites-enabled/{{ object.unique_ident }} ]]; then
            rm /etc/apache2/sites-enabled/{{ object.unique_ident }}
            #TODO: if configtest goes wrong, send email to admin
            if [[ $(apache2ctl configtest) ]]; then
                /etc/init.d/apache2 reload
            fi
        fi
    {% endif %}
else
    rm /tmp/{{ object.unique_ident }}
fi


if [[ ! -e $FCGI_DIR ]]; then
    mkdir $FCGI_DIR
fi

echo -e '#!/bin/sh
# Wrapper for PHP-fcgi
# This wrapper can be used to define settings before launching the PHP-fcgi binary.
# Define the path to php.ini. This defaults to /etc/php{{ object.php.version }}/cgi.
#export PHPRC=/etc/php{{ object.php.version }}/cgi
# Define the number of PHP childs that will be launched. Leave undefined to let PHP decide.
#export PHP_FCGI_CHILDREN=3
# Maximum requests before a process is stopped and a new one is launched
#export PHP_FCGI_MAX_REQUESTS=5000
# Launch the PHP CGI binary
# This can be any other version of PHP which is compiled with FCGI support.
exec /usr/bin/php{{ object.php.version }}-cgi {% for directive in object.php.directives %}-d {{ directive.name }}="{{ directive.value }}" {% endfor %}
' > ${FCGI_DIR}/php-fcgi-wrapper

chown -R ${USER}:${GROUP} ${FCGI_DIR}

if [[ ! -e ${CGI_DIR} ]]; then
    cp -R --preserve=all /home/pangea/skeleton/cgi-bin.skeleton/ ${CGI_DIR}
    sed -i "s/pangea\.org/{{ object.ServerName }}/g" ${CGI_DIR}/captcha/hv.cgi
    chown -R ${USER}:${GROUP} ${CGI_DIR}
fi



{% if object.fcgid.directives %}

    FCGI_CONF_NAME="fcgi-${USER}-{{ object.unique_ident}}.conf"
    FCGI_CONF="/etc/apache2/conf.d/${FCGI_CONF_NAME}"    
    {% gapless %} 

    echo -e "<IfModule mod_fcgid.c>
    FcgidCmdOptions ${FCGI_DIR}/php-fcgi-wrapper \\
    {% for directive in object.fcgid.directives %}
        {{ directive.name }} {{ directive.value }} \\
    {% endfor %}
</IfModule>
" > /tmp/${FCGI_CONF_NAME}

    {% endgapless %}

    if [[ ! -e ${FCGI_CONF} || $(diff /tmp/${FCGI_CONF_NAME} ${FCGI_CONF}) ]]; then
        mv /tmp/${FCGI_CONF_NAME} ${FCGI_CONF}
        /etc/init.d/apache2 reload
    else
        rm /tmp/${FCGI_CONF_NAME}
    fi

{% endif %}
