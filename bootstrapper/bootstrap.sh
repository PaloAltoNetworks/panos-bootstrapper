#!/usr/bin/env sh
# Simple wrapper script around the flask CLI support
# useful for calling directly via a docker image when a microservice isn't an option
#
# nembery@paloaltonetworks.com 10-15-18
#
#

CMD=$1
export FLASK_APP=/app/bootstrapper/bootstrapper_cli.py
shift
echo flask ${CMD} "$@"
flask ${CMD} "$@"
