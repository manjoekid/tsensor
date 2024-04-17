#!/bin/bash
sudo git stash
sudo git pull
sudo chown -R root:www-data /home/tsensor/tsensor/tsensor_py/ || echo "Failed to change permissions."
sudo chmod -R 775 /home/tsensor/tsensor/tsensor_py/ || echo "Failed to change permissions."
sudo ./virtualenv_py/bin/python3 ./test_serial.py