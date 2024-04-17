#!/bin/bash
git stash
git pull
chown -R root:www-data /home/tsensor/tsensor/tsensor_py/ || echo "Failed to change permissions."
chmod -R 775 /home/tsensor/tsensor/tsensor_py/ || echo "Failed to change permissions."
/home/tsensor/tsensor/tsensor_py/virtualenv_py/bin/python3 /home/tsensor/tsensor/tsensor_py/test_serial.py