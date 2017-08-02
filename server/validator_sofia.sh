#!/usr/bin/env bash

# Forwards arguments from the BOINC script_validator to validator.py
validator.py --app sofia ${@:2}
exit $?