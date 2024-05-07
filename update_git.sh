#!/bin/bash

# Function to download files from GitHub repository
update_git() {
    # Define repository URL
    repo_url="https://github.com/manjoekid/tsensor"

    # Define destination folder
    destination_folder="/home/tsensor/"

    echo "Updating Git repository..."
    cd  /home/tsensor/tsensor || { echo "Error: Folder not found."; exit 1; }

    echo "Reseting local repository..."
    sudo git reset || { echo "Erro: Não conseguiu resetar o repositório local."; exit 1; }

    sudo git stash push --include-untracked || { echo "Erro: Não conseguiu resetar o repositório local."; exit 1; }
    sudo git stash drop || { echo "Erro: Não conseguiu resetar o repositório local."; exit 1; }

    # Download repository files
    echo "Pulling repository from GitHub..."
    sudo git pull || { echo "Erro: Não conseguiu dar o pull no repositório do Github."; exit 1; }
    
    echo "Repository pulled successfully."

    echo "Buscando variáveis de ambiente..."
    sudo cp /home/tsensor/.env_saved /home/tsensor/tsensor/tsensor_py/.env

}

reinstall_all(){
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

    sudo chown -R root:www-data /home/tsensor/tsensor/tsensor_py/ || echo "Failed to change permissions."
    sudo chmod -R 775 /home/tsensor/tsensor/tsensor_py/ || echo "Failed to change permissions."

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

    echo "Deactivating virtual environment..."
    deactivate
    echo "Virtual environment deactivated successfully." 

    echo "Starting tsensor web service..."
    sudo cp flask.service /etc/systemd/system/  || { echo "Failed to start tsensor web service. Exiting."; exit 1; } 

    sudo chown -R root:www-data /home/tsensor/tsensor/tsensor_web/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }
    sudo chmod -R 775 /home/tsensor/tsensor/tsensor_web/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }


}


stop_service() {
    sudo systemctl stop tsensor || { echo "Erro: Não encontrou serviço tsensor."; exit 1; }
    sudo systemctl stop flask || { echo "Erro: Não encontrou serviço flask."; exit 1; }
    echo "Serviços parados."

    echo "Salvando variáveis de ambiente..."
    sudo cp /home/tsensor/tsensor/tsensor_py/.env /home/tsensor/.env_saved 

}

start_service() {
    sudo systemctl start tsensor || { echo "Erro: Não subiu serviço tsensor."; exit 1; }

    sudo systemctl daemon-reload   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

    sudo systemctl start flask   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }
    sudo systemctl enable flask   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

    sudo cp flask.conf /etc/nginx/conf.d/   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

    sudo nginx -t   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

    sudo systemctl restart nginx   || { echo "Failed to start tsensor web service. Exiting."; exit 1; }

    sudo systemctl start flask || { echo "Erro: Não subiu serviço flask."; exit 1; }
    echo "Serviços iniciados."
}


echo "Iniciando atualização do repositório Git..."

# Call the functions
stop_service
update_git
reinstall_all
start_service

echo "Atualização realizada com sucesso."
