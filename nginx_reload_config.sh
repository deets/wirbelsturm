#!/bin/bash
# use this from within the wirbelsturm base directory

kill -SIGHUP `cat nginx/nginx.pid`