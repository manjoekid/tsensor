#!/bin/bash

# Function to download files from GitHub repository
download_files() {
    # Define repository URL
    repo_url="https://github.com/manjoekid/tsensor"

    # Define destination folder
    destination_folder="/home/tsensor/"

    # Create destination folder if it doesn't exist
    mkdir -p "$destination_folder"

    # Download repository files
    echo "Cloning repository from GitHub..."
    git clone "$repo_url"
    
    echo "Repository cloned successfully."
}

# Function to run another script
run_script() {
    # Change directory to the downloaded files folder
    cd  /home/tsensor/tsensor || { echo "Error: Folder not found."; exit 1; }

    # Run another script
    echo "Running installation script..."
    bash setup_tsensor.sh || { echo "Error: setup finished with error."; exit 1; }
    echo "Script executed successfully."
}

# Call the functions
download_files
run_script