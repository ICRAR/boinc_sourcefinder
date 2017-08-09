#!/usr/bin/env bash

# Forwards arguments from the BOINC script_validator to validator.py
SCRIPT_PATH=$( cd $(dirname $0) ; pwd -P )
${SCRIPT_PATH}/../validator.py compare --app sofia ${@:1}
exit $?