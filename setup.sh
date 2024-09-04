#!/bin/bash

# Check if inky directory exists
if [ -d "inky" ]; then
    echo "inky directory already exists. Removing..."
    rm -rf inky
fi

# Clone inky repository
git clone https://github.com/pimoroni/inky.git

# Create and activate virtual environment
python3 -m venv spotipi_env
source spotipi_env/bin/activate

# Install required Python packages
pip install spotipy pillow inky

# Prompt for Spotify credentials
echo "Enter your Spotify Client ID:"
read client_id
echo "Enter your Spotify Client Secret:"
read client_secret
echo "Enter your Spotify Redirect URI:"
read redirect_uri
echo "Enter your spotify username:"
read spotify_username

# Generate Spotify token
echo "Generating Spotify token..."
python python/generateToken.py $spotify_username
if [ $? -ne 0 ]; then
    echo "Error: Failed to generate Spotify token. Check your credentials and try again."
    exit 1
fi

echo
echo "###### Spotify Token Created ######"
echo "Filename: .cache"

if [ ! -f ".cache" ]; then
    echo "Error: .cache file not found. Token generation may have failed."
    exit 1
fi

echo "Enter the full path to your spotify token:"
read spotify_token_path

# ... rest of your existing script ...

# Deactivate virtual environment
deactivate

echo "Removing spotipi service if it exists:"
sudo systemctl stop spotipi
sudo rm -rf /etc/systemd/system/spotipi.*
sudo systemctl daemon-reload
echo "...done"

echo "Creating spotipi service:"
sudo cp ./config/spotipi.service /etc/systemd/system/
sudo sed -i -e "/\[Service\]/a ExecStart=python ${install_path}/python/displayCoverArt.py ${spotify_username} ${spotify_token_path}" /etc/systemd/system/spotipi.service
sudo mkdir /etc/systemd/system/spotipi.service.d
spotipi_env_path=/etc/systemd/system/spotipi.service.d/spotipi_env.conf
sudo touch $spotipi_env_path
sudo echo "[Service]" >> $spotipi_env_path
sudo echo "Environment=\"SPOTIPY_CLIENT_ID=${spotify_client_id}\"" >> $spotipi_env_path
sudo echo "Environment=\"SPOTIPY_CLIENT_SECRET=${spotify_client_secret}\"" >> $spotipi_env_path
sudo echo "Environment=\"SPOTIPY_REDIRECT_URI=${spotify_redirect_uri}\"" >> $spotipi_env_path
sudo systemctl daemon-reload
sudo systemctl start spotipi
sudo systemctl enable spotipi
echo "...done"

echo "SETUP IS COMPLETE"
