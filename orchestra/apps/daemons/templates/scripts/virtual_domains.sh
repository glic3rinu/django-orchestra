#!/bin/bash

VIRTDOMAIN_FILE=/etc/postfix/virtdomains

{% if object.virtualdomain %}
    echo 'created {{ object }}' >> /tmp/99
    if [[ ! $(grep "^{{ object }}$" $VIRTDOMAIN_FILE) ]]; then
        echo "{{ object }}" >> $VIRTDOMAIN_FILE;
        /etc/init.d/postfix reload
    fi
{% else %}
    echo 'deleted {{ object }}' >> /tmp/99
    if [[ $(grep "^{{ object }}$" $VIRTDOMAIN_FILE) ]]; then
        sed -i "/^{{ object }}$/d" $VIRTDOMAIN_FILE;
        /etc/init.d/postfix reload
    fi
{% endif %}
