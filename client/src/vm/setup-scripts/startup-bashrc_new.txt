# ~/.bashrc: executed by bash(1) for non-login shells.

# Note: PS1 and umask are already set in /etc/profile. You should not
# need this unless you want different defaults for root.
# PS1='${debian_chroot:+($debian_chroot)}\h:\w\$ '
# umask 022

# You may uncomment the following lines if you want `ls' to be colorized:
# export LS_OPTIONS='--color=auto'
# eval "`dircolors`"
# alias ls='ls $LS_OPTIONS'
# alias ll='ls $LS_OPTIONS -l'
# alias l='ls $LS_OPTIONS -lA'
#
# Some more alias to avoid making mistakes:
# alias rm='rm -i'
# alias cp='cp -i'
# alias mv='mv -i'

# BOINC VM Initialization
echo BOINC VM Initialization [Sleeping 5 seconds] | vboxmonitor
sleep 5

echo -- Mounting shared directory | vboxmonitor
mount -t vboxsf shared /root/shared
if [ $? -ne 0 ]; then
    echo ---- Failed to mount shared directory | vboxmonitor
    sleep 5
    shutdown -hP 0
fi

echo -- Launching Application
if [ -f /root/run_duchamp.py ]; then
    echo -- in /root directory | vboxmonitor
    mkdir -p /root/shared/worker # input files are copied in here and duchamp is run from worker/parameter_files_X
    mkdir -p /root/shared/log # log file is written to in here
    mkdir -p /root/shared/outputs # output files put here
    #cp -r /root/shared/*.gz /root/shared/worker # move the tar.gz input files in to the worker directory
    #echo --- Application has been moved the the worker directory | vboxmonitor
    #sleep 2
    cd /root/shared/worker
    echo -- About to execute run_duchamp.py | vboxmonitor
    sleep 2
    python /root/run_duchamp.py | vboxmonitor
	# process ended, but did it actually fully complete?
    if [ -f /root/completed ]; then
        cd /root
        rm -rf /root/shared/worker
        # This is done in python code now md5sum /root/shared/outputs/data_collection.csv > /root/shared/outputs/md5check.txt
        cp /root/shared/log/Log.txt /root/shared/outputs
        cd /root/shared
        tar -cvzf outputs.tar.gz outputs/data_collection.csv outputs/hash.md5 outputs/Log.txt
        echo --- output directory has been zipped! | vboxmonitor
        echo --- Removing everything unneeded | vboxmonitor
        sleep 5
        ls | grep -v outputs.tar.gz | xargs rm -rf
        echo --- Everything has gone according to plan | vboxmonitor
        sleep 5
        shutdown -hP 0
    else
	# process did not fully complete, just restart at our checkpoint again later
        echo ---VM suspend or shutdown, continuing later.. | vboxmonitor
        sleep 5
        shutdown -hP 0
    fi
else
       echo ---- Failed to launch script | vboxmonitor
       sleep 5
       shutdown -hP 0
fi