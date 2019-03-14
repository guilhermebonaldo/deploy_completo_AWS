#!/bin/bash

url=$1
payload=$2
content=${3:-text/csv}

C:/curl --data-binary @${payload} -H "Content-Type: ${content}" -v ${url}/invocations
