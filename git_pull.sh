#!/bin/bash
cd /home/tsensor/tsensor/
sudo git stash
sudo git pull
sudo chown -R root:www-data /home/tsensor/tsensor/tsensor_py/ 
sudo chmod -R 775 /home/tsensor/tsensor/tsensor_py/ 
sudo /home/tsensor/tsensor/tsensor_py/virtualenv_py/bin/python3 /home/tsensor/tsensor/tsensor_py/test_serial.py