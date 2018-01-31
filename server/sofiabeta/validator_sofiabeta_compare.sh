#!/usr/bin/env bash

# Forwards arguments from the BOINC script_validator to validator.py
/home/ec2-user/boinc_sourcefinder/server/validator.py compare --app sofiabeta ${@:1}
exit $?