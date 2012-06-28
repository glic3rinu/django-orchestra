#!/bin/bash

# Find all the files from an specific owner and sum their bytes

USERNAME="{{ object.user.username }}"
RESULT=$(find /home/pangea/ -type f -user $USERNAME -exec du -s {} \;|awk {'sum+=$1'}END{'print sum'})

if [[ ! $RESULT ]]; then
    echo 0
else
    echo $RESULT
fi
