#!/bin/bash

if [[ $(list_lists -b|grep "^{{ object.name }}$") ]]; then
    rmlist {{ object.name }}
fi


#TODO remove archive. Also check if a removed list has archive and delete them too.

