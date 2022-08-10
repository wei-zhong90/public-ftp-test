#!/bin/bash

docker run --env-file env.list -v /home/ec2-user/nginx/log:/var/log/nginx -p 21:21 -p 8192:8192 -p 8193:8193 -p 8194:8194 -p 8195:8195 -p 8196:8196 -p 8197:8197 -p 8198:8198 -p 8199:8199 -p 8200:8200 new-proxy