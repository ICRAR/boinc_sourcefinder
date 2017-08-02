#!/usr/bin/env bash

# Forwards arguments from the BOINC script_validator to validator.py
validator.py --app duchamp ${@:2}
exit $?