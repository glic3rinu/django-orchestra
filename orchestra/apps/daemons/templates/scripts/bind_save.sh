#!/bin/bash

echo -e "{{ object.origin }}.  IN  SOA {{ object.primary_ns }}. {{ object.hostmaster_email }}. (
\t\t{{ object.serial }}\t; serial number
\t\t{{ object.slave_refresh }}\t; slave refresh
\t\t{{ object.slave_retry }}\t; slave retry time in case of problem
\t\t{{ object.slave_expiration }}\t; slave expiration time
\t\t{{ object.min_caching_time }}\t; maximum caching time in case of failed lookups
\t\t)
{% for record in object.record_set.all %}
{{ record.name }}\t\tIN\t{{ record.type }}\t{{ record.data }}{% endfor %}" > /etc/bind/master/{{ object.origin }}


if ! [[ $(grep '"{{ object.origin }}"' /etc/bind/primarios-pangea.conf) ]]; then
    echo 'zone "{{ object }}" { 
	type master; 
	file "/etc/bind/master/{{ object }}"; 
};' >> /etc/bind/primarios-pangea.conf 
fi

rndc reload

exit 0;
