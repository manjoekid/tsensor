#!/bin/bash

cd /home/tsensor/tsensor/tsensor_py || { echo "Failed to change directory. Exiting."; exit 1; }

echo "Changing permissions for the tsensor service..."
chmod +x tsensor_py_service.sh || echo "Failed to change permissions."

sudo chown -R root:www-data /home/tsensor/tsensor/tsensor_py/ || echo "Failed to change permissions."
sudo chmod -R 775 /home/tsensor/tsensor/tsensor_py/ || echo "Failed to change permissions."

echo "Starting tsensor service..."
sudo cp tsensor.service /etc/systemd/system/ || echo "Failed to start tsensor service."
sudo systemctl stop tsensor.service || echo "Failed to start tsensor service."
sudo systemctl enable tsensor.service || echo "Failed to start tsensor service."
sudo systemctl start tsensor.service || echo "Failed to start tsensor service."

echo "Tsensor finished. Starting web server installation..."
cd /home/tsensor/tsensor/tsensor_web || { echo "Failed to change directory. Exiting."; exit 1; }


echo "Starting tsensor web service..."
sudo cp flask.service /etc/systemd/system/  || { echo "Failed to start tsensor web service. Exiting."; exit 1; } 

sudo chown -R root:www-data /home/tsensor/tsensor/tsensor_web/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }
sudo chmod -R 775 /home/tsensor/tsensor/tsensor_web/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo systemctl daemon-reload   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo systemctl stop flask
sudo systemctl start flask   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }
sudo systemctl enable flask   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo cp flask.conf /etc/nginx/conf.d/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo nginx -t   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo systemctl restart nginx   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }
