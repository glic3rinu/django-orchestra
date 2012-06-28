#!/bin/bash

echo -e "<VirtualHost {{ object.ip }}:{{ object.port }}>
	DocumentRoot {{ object.DocumentRoot }}
	ServerName {{ object.ServerName }}
	ServerAlias {{ object.ServerAlias }}
	CustomLog {{ object.CustomLog }}
	
	SuexecUserGroup marcay pangea
	Action php-fcgi /fcgi-bin/php-fcgi-wrapper

    {{ object.rendered_custom_directives }}
    Deeeeeeeeeeeeeeeeeeeeeeeeleted
</VirtualHost>" > /tmp/{{ object.unique_ident }}


