#!/bin/bash

echo "Installing sudo..."
su -c 'apt install sudo'
su -c 'newgrp sudo'
su -c '/usr/sbin/useradd tsensor sudo'

su -c '/usr/sbin/usermod -aG sudo tsensor'

su -c 'newgrp tsensor'

