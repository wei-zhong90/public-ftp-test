#!/bin/bash

nginx_path="/etc/nginx/nginx.conf"


# Setting IFS (input field separator) value as ","
IFS=','

# Reading the split string into array
read -ra arr <<< "$IP_ADDR_LIST"

if [ ${#arr[@]} -eq 0 ];
then
  echo "Need an non-empty list of ips separated by comma";
  exit 1;
fi

server=""
for val in "${arr[@]}";
do
  server=$server`echo "server <IP_ADDR>:<PORT> max_fails=0 fail_timeout=10s;\n" | sed -e "s/<IP_ADDR>/$val/g"`
done

upstream_content=""

for port in {8192..8200};
do
  upstream_content=$upstream_content`echo "upstream port<PORT> {\nleast_conn;\n$server}\n" | sed -e "s/<PORT>/$port"/g`
done

for port in {21,22};
do
  upstream_content=$upstream_content`echo "upstream port<PORT> {\nleast_conn;\n$server}\n" | sed -e "s/<PORT>/$port"/g`
done

sed -i "/#INSERT UPSTREAM CONTENT/a $upstream_content" $nginx_path

read -ra arr <<< "$DENY_LIST"

if [ ${#arr[@]} -eq 0 ];
then
  echo "No IPs are going to be denied";
  cat $nginx_path;
  exit 0;
else
  for val in "${arr[@]}";
  do
    sed -i "/#INSERT DENY LIST/a deny\t$val;" $nginx_path
  done
fi

cat $nginx_path