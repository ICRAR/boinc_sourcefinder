#@IgnoreInspection BashAddShebang
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

export SOFIA_MODULE_PATH="/root/SoFiA/build/lib.linux-x86_64-2.7"
export SOFIA_PIPELINE_PATH="/root/SoFiA/sofia_pipeline.py"
export PATH="$PATH:/root/SoFiA"

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
mkdir -p /root/shared/inputs # input files put here
mkdir -p /root/shared/outputs # output files put here
python run_sofia.py
echo -- Application complete, shutting down.
sleep 5
shutdown -hP 0