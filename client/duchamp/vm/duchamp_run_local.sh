#!/bin/bash

export LD_LIBRARY_PATH="/usr/local/lib"
echo -- Launching Application
if [ -f /root/run_duchamp.py ]; then
    echo -- in /root directory
    mkdir -p /root/worker
    cp -r /root/shared/* /root/worker
    echo --- Application has been moved the the worker directory
    sleep 2
    cd /root/
    echo -- in Worker directory
    sleep 2
    python run_duchamp.py
	# process ended, but did it actually fully complete?
    if [ -f /root/completed ]; then
        cd /root
        cp -r worker/* shared/
        rm -rf /root/worker
        cp data_retrieval.py shared/outputs
        cd shared/outputs
        python data_retrieval.py
        cd /root/shared
        md5sum final_output.txt > md5check.txt
        tar -cvzf outputs.tar.gz outputs/data_collection.csv
        echo --- output directory has been zipped!
        sleep  5
        echo --- Everything has gone according to plan
        sleep 5
        #shutdown -hP 0
    else
	# process did not fully complete, just restart at our checkpoint again later
        echo ---VM suspend or shutdown, continuing later..
    fi
else
       echo ---- Failed to launch script
       sleep 5
       #shutdown -hP 0
fi
