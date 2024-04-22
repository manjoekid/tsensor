#!/bin/bash


sudo apt install gpsd chrony -y
sudo systemctl start chronyd


sudo cp gpsd /etc/default/gpsd
sudo cp chrony.conf /etc/chrony/chrony.conf


#sudo gpsd -s 115200 -D 5 -N -n /dev/ttyUSB0



