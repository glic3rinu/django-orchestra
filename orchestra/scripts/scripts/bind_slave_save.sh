#!/bin/bash

if [[ $(grep 'zone "{{ object.origin }}"' /etc/bind/secundarios-pangea.conf ) ]]; then
    echo -e 'zone "{{ object.origin }}" {
	    type slave;
	    file "{{ object.origin }}";
	    masters{
	 	       77.246.179.81;
	    };
};' >> /etc/bind/secundarios-pangea.conf 
fi


