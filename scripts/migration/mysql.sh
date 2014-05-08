#!/bin/bash


QUERY="select db,db.user,user.user,password from user left join db on user.user=db.user;"

mysql mysql -sN -e "$QUERY" | while read line; do
    DBNAME=$(echo "$line" | awk {'print $1'})
    OWNER=$(echo "$line" | awk {'print $2'})
    USER=$(echo "$line" | awk {'print $3'})
    PASSWORD=$(echo "$line" | awk {'print $4'})
    if OWNER
