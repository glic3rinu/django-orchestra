#!/bin/bash

echo 'merda' > /tmp/999

if [[ ! $(list_lists -b|grep "^{{ object.name }}$") ]]; then
    echo 'yes' >> /tmp/999
    echo "{{ object.domain }}" >> /tmp/999
    echo "{{ object.name }}" >> /tmp/999
    echo "{{ object.admin }}" >> /tmp/999
    echo "{{ object.password }}" >> /tmp/999
    echo "newlist -l es --emailhost={{ object.domain }} {{ object.name }} {{ object.admin }} {{ object.password }}" >> /tmp/999
    echo "\n"|newlist -l es --emailhost={{ object.domain }} {{ object.name }} {{ object.admin }} {{ object.password }}
fi
    
    
    
    

