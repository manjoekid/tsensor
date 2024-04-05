#!/bin/bash
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
sudo cp ./interfaces-updated  /etc/network/interfaces || { echo "Falhou a cópia do arquivo de interfaces. Exiting."; exit 1; }


echo "reiniciando a rede"
sudo systemctl restart networking || { echo "Failed to restart networking. Exiting."; exit 1; }

echo "tsensor script executed successfully."