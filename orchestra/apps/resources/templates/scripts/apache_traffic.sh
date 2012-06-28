#!/bin/bash

LOG_FILES="/var/log/apache2/virtual/{{ object.ServerName }}"
# start_date and end_date expected format: YYYYMMDDhhmmss

function get_traffic(){
    awk 'BEGIN {
        ini = "{{ start_date|date:"YmdHis" }}"; 
        end = "{{ end_date|date:"YmdHis" }}";
               
        months["Jan"]="01"; 
        months["Feb"]="02"; 
        months["Mar"]="03"; 
        months["Apr"]="04"; 
        months["May"]="05";
        months["Jun"]="06"; 
        months["Jul"]="07"; 
        months["Aug"]="08"; 
        months["Sep"]="09"; 
        months["Oct"]="10"; 
        months["Nov"]="11";
        months["Dec"]="12"; }
    { 
        date = substr($4,2)
        year = substr(date,8,4) 
        month = months[substr(date,4,3)];   
        day = substr(date,1,2) 
        hour = substr(date,13,2) 
        minute = substr(date,16,2) 
        second = substr(date,19,2); 
        line_date = year month day hour minute second
        if ( line_date > ini && line_date < end)
            if ( $10 == "" ) 
                sum+=$9
            else
                sum+=$10; 
        }
    END {
    print sum;
    }' $LOG_FILES
}

RESULT=$(get_traffic)

if [[ $RESULT ]]; then 
    echo $RESULT
else
    echo 0
fi

return 0
