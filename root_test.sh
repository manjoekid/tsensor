#!/bin/bash

echo "Installing sudo..."
su -c 'apt install sudo'
su -c 'useradd tsensor sudo'
newgrp tsensor
newgrp sudo
