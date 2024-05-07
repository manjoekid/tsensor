#!/bin/bash

#echo "Installing sudo..."
#su root -c 'apt install sudo'
#newgrp sudo
#su -c '/usr/sbin/useradd tsensor sudo'
#newgrp tsensor

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
pip3 install pyserial numpy shared-memory-dict pyModbusTCP python-dotenv || { echo "Failed to install Python packages. Exiting."; deactivate; exit 1; }
echo "Python packages installed successfully."

echo "Deactivating virtual environment..."
deactivate
echo "Virtual environment deactivated successfully." 

echo "Changing permissions for the tsensor service..."
chmod +x tsensor_py_service.sh || echo "Failed to change permissions."
sudo cp /home/tsensor/tsensor/.env_linux /home/tsensor/tsensor/tsensor_py/.env

sudo chown -R root:www-data /home/tsensor/tsensor/tsensor_py/ || echo "Failed to change permissions."
sudo chmod -R 775 /home/tsensor/tsensor/tsensor_py/ || echo "Failed to change permissions."

echo "Starting tsensor service..."
sudo cp tsensor.service /etc/systemd/system/ || echo "Failed to start tsensor service."
sudo systemctl enable tsensor.service || echo "Failed to start tsensor service."
sudo systemctl start tsensor.service || echo "Failed to start tsensor service."

echo "Tsensor finished. Starting web server installation..."
cd /home/tsensor/tsensor/tsensor_web || { echo "Failed to change directory. Exiting."; exit 1; }


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
pip3 install wheel gunicorn flask numpy shared-memory-dict python-dotenv || { echo "Failed to install Python packages. Exiting."; deactivate; exit 1; }
echo "Python packages installed successfully."

#echo "Testing gunicorn..."
#gunicorn --bind 0.0.0.0:5000 wsgi:app

echo "Deactivating virtual environment..."
deactivate
echo "Virtual environment deactivated successfully." 


echo "Starting tsensor web service..."
sudo cp flask.service /etc/systemd/system/  || { echo "Failed to start tsensor web service. Exiting."; exit 1; } 

sudo chown -R root:www-data /home/tsensor/tsensor/tsensor_web/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }
sudo chmod -R 775 /home/tsensor/tsensor/tsensor_web/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo systemctl daemon-reload   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo systemctl start flask   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }
sudo systemctl enable flask   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo cp flask.conf /etc/nginx/conf.d/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo nginx -t   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

sudo systemctl restart nginx   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

echo "Installing bridge-utils..."
sudo apt install bridge-utils  || { echo "Failed to install bridge-utils. Exiting."; exit 1; }


echo "Installing bridge - sudo brctl addbr br0"
sudo brctl addbr br0  || { echo "Failed to create bridge. Exiting."; exit 1; }


#sudo ip addr show
sudo brctl addif br0 enp1s0 enp2s0 || { echo "Failed to create bridge. Exiting."; exit 1; }
#sudo brctl show

echo "Tentando subir rede - sudo ifup enp2s0"
sudo ifup enp2s0 || echo "Falhou enp2s0, verifique conexões."


echo "copiando novo arquivo de interfaces"
sudo cp /home/tsensor/tsensor/interfaces-updated  /etc/network/interfaces || { echo "Falhou a cópia do arquivo de interfaces. Exiting."; exit 1; }


echo "reiniciando a rede"
sudo systemctl restart networking || { echo "Failed to restart networking. Exiting."; exit 1; }

echo "tsensor script executed successfully."