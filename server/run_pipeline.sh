#!/usr/bin/env bash

# This runs the whole work generation pipeline for a specified run ID.
# It creates the run ID, registers all current parameters to it, registers cubes, then generates work units.

python register_run.py --app $1 $2
python register_cube.py --app $1 $2
python work_generator.py --app $1 $2

echo "Pipeline complete."