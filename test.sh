#!/bin/bash

su root -c 'adduser tsensor sudo'

apt install sudo
su tsensor



echo "Changing directory to tsensor_py..."
cd tsensor_py || { echo "Failed to change directory. Exiting."; exit 1; }
echo "Directory changed successfully."

echo "Installing necessary packages..."
sudo apt install -y python3-venv python3-pip || { echo "Failed to install packages. Exiting."; exit 1; }
echo "Packages installed successfully."

echo "Creating and activating virtual environment..."
python3 -m venv virtualenv_py || { echo "Failed to create virtual environment. Exiting."; exit 1; }
source virtualenv_py/bin/activate || { echo "Failed to activate virtual environment. Exiting."; exit 1; }
echo "Virtual environment created and activated successfully."

echo "Installing required Python packages..."
pip3 install pyserial numpy shared-memory-dict pyModbusTCP || { echo "Failed to install Python packages. Exiting."; deactivate; exit 1; }
echo "Python packages installed successfully."

echo "Deactivating virtual environment..."
deactivate
echo "Virtual environment deactivated successfully." 

echo "Changing permissions for the tsensor service..."
chmod +x tsensor_py_service.sh || echo "Failed to change permissions."

sudo chown -R root:www-data /home/tsensor/tsensor_py/ || echo "Failed to change permissions."
sudo chmod -R 775 /home/tsensor/tsensor_py/ || echo "Failed to change permissions."

echo "Starting tsensor service..."
sudo cp tsensor.service /etc/systemd/system/ || echo "Failed to start tsensor service."
sudo systemctl enable tsensor.service || echo "Failed to start tsensor service."
sudo systemctl start tsensor.service || echo "Failed to start tsensor service."

echo "Tsensor finished. Starting web server installation..."
cd /home/tsensor/tsensor_web || { echo "Failed to change directory. Exiting."; exit 1; }


echo "Installing necessary packages..."
sudo apt install -y python3-venv python3-pip || { echo "Failed to install packages. Exiting."; exit 1; }
sudo apt-get install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
echo "Packages installed successfully."


echo "Creating and activating virtual environment..."
python3 -m venv virtualenv_web || { echo "Failed to create virtual environment. Exiting."; exit 1; }
source virtualenv_web/bin/activate || { echo "Failed to activate virtual environment. Exiting."; exit 1; }
echo "Virtual environment created and activated successfully."

echo "Installing required Python packages..."
pip3 install wheel gunicorn flask numpy shared-memory-dict  || { echo "Failed to install Python packages. Exiting."; deactivate; exit 1; }
echo "Python packages installed successfully."

echo "Testing gunicorn..."
gunicorn --bind 0.0.0.0:5000 wsgi:app

echo "Deactivating virtual environment..."
deactivate
echo "Virtual environment deactivated successfully." 


echo "Starting tsensor web service..."
sudo cp flask.service /etc/systemd/system/  || { echo "Failed to start tsensor web service. Exiting."; exit 1; } 

sudo chown -R root:www-data /home/tsensor/tsensor_web/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }
sudo chmod -R 775 /home/tsensor/tsensor_web/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo systemctl daemon-reload   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo systemctl start flask   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }
sudo systemctl enable flask   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo cp flask.conf /etc/nginx/conf.d/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo nginx -t   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo systemctl restart nginx   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

echo "tsensor script executed successfully."