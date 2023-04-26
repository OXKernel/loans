#!/usr/bin/bash
# To test docs:
# http://127.0.0.1:8000/docs
#
curl "http://127.0.0.1:8000/create/user?id=someuser"
printf "\n";
curl "http://127.0.0.1:8000/create/loan?id=123"
printf "\n";
