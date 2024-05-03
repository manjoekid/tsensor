curl -O https://raw.githubusercontent.com/manjoekid/tsensor/main/start_tsensor.sh
chmod +x start_tsensor.sh
./start_tsensor.sh


Linux

Adiciona tsensor no sudoers group

su -
adduser tsensor sudo
apt install sudo
su tsensor

deslogar e logar novamente para adduser fazer efeito

copiar os arquivos para pasta tsensor


Instalar test_serial.py

cd tsensor_py

sudo apt install python3-venv python3-pip

python3 -m venv virtualenv_py
source virtualenv_py/bin/activate


pip3 install pyserial
pip3 install numpy
pip3 install shared-memory-dict
pip3 install pyModbusTCP

deactivate

sudo ./virtualenv_py/bin/python3 test_serial.py

<verifique se funciona>

--se tiver problema com permissão shm - https://stackoverflow.com/questions/2009278/python-multiprocessing-permission-denied


chmod +x tsensor_py_service.sh


sudo chown -R root:www-data /home/tsensor/tsensor_py/
sudo chmod -R 775 /home/tsensor/tsensor_py/


sudo cp tsensor.service /etc/systemd/system/
sudo systemctl enable tsensor.service
sudo systemctl start tsensor.service
sudo systemctl status tsensor.service



Web 

Instalar test_web.py

https://www.rosehosting.com/blog/how-to-install-flask-on-debian-12/
https://www.rosehosting.com/blog/how-to-deploy-flask-application-with-nginx-and-gunicorn-on-ubuntu-20-04/


cd tsensor_web
apt install python3-venv python3-pip
apt-get install nginx -y
systemctl start nginx
systemctl enable nginx

python3 -m venv virtualenv_web
source virtualenv_web/bin/activate
pip3 install wheel
pip3 install gunicorn flask
pip3 install shared-memory-dict
pip3 install numpy

gunicorn --bind 0.0.0.0:5000 wsgi:app

resultado esperado:
[2021-12-23 10:37:15 +0000] [9352] [INFO] Starting gunicorn 20.1.0
[2021-12-23 10:37:15 +0000] [9352] [INFO] Listening at: http://0.0.0.0:5000 (9352)
[2021-12-23 10:37:15 +0000] [9352] [INFO] Using worker: sync
[2021-12-23 10:37:15 +0000] [9354] [INFO] Booting worker with pid: 9354


deactivate

sudo cp flask.service /etc/systemd/system/

sudo chown -R root:www-data /home/tsensor/tsensor_web/
sudo chmod -R 775 /home/tsensor/tsensor_web/

sudo systemctl daemon-reload

sudo systemctl start flask
sudo systemctl enable flask

sudo systemctl status flask

sudo cp flask.conf /etc/nginx/conf.d/

sudo nginx -t

sudo systemctl restart nginx


Bridge

sudo apt install bridge-utils
sudo brctl addbr br0
sudo ip addr show
sudo brctl addif br0 enp1s0 enp2s0
sudo brctl show
sudo ifup enp2s0







Débitos técnicos
criar um novo arquivo python para análise dos dados
tratar leituras vazias
mudar o alarme para tempo ao invés de quantidade de amostras
a média só é calculada depois da primeira leitura, enquanto isso o sistema entende que é zero e alarma
usar variáveis de ambiente para receber os parametros de inicialização do sistema
escrever script de instalação
avaliar uso do docker

to do
alterar limites apresentados na tela dependendo do selecionado no configurador
enviar log junto com csv
criar bash script para atualizar código
verificar circularBuffer temperatures.js linha 135