#!/bin/bash

echo "Installing sudo..."
su -c 'apt install sudo'
newgrp sudo
su -c '/usr/sbin/useradd tsensor sudo'
newgrp tsensor

