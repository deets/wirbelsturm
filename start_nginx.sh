#!/bin/bash
# use this from within the wirbelsturm base directory

# we need a trailing slash, otherwise nginx pukes
nginx -p `pwd`/ -c nginx.conf 