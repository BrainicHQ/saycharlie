#!/bin/bash

#
#  Copyright (c) 2024 by Silviu Stroe (brainic.io)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#  Created on 5/16/24, 9:02 PM
#
#  Author: Silviu Stroe
#

# Define the application's directory with an absolute path
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Starting the installation of the saycharlie SVX Dashboard..."

# Install Python 3, pip, and python3-venv if they are not already installed
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is not installed. Installing Python 3..."
    sudo apt-get update && sudo apt-get install python3 -y
fi

if ! command -v pip3 &>/dev/null; then
    echo "pip3 is not installed. Installing pip3..."
    sudo apt-get install python3-pip -y
fi

if ! dpkg -s python3-venv &>/dev/null; then
    echo "python3-venv is not installed. Installing python3-venv..."
    sudo apt-get install python3-venv -y
fi

# Update pip to the latest version
echo "Updating pip to the latest version..."
sudo pip3 install --upgrade pip

# Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv "$APP_DIR/venv"
echo "Virtual environment created."

# Activate the virtual environment
source "$APP_DIR/venv/bin/activate"

# Install requirements
echo "Installing dependencies from requirements.txt..."
pip install -r "$APP_DIR/requirements.txt"
echo "Dependencies installed."

# Creating a systemd service file
SERVICE_FILE=/etc/systemd/system/saycharlie.service
echo "Creating a systemd service file at $SERVICE_FILE"

# Requires superuser access
sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=saycharlie SVX Dashboard
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="FLASK_APP=app.py"
ExecStart=$APP_DIR/venv/bin/flask run --host=0.0.0.0 --port=8337

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable saycharlie.service

# Start the service
sudo systemctl start saycharlie.service

echo "saycharlie service has been started and enabled at boot."

LOCAL_IP=$(hostname -I | awk '{print $1}') # Get the local IP address

# Provide final confirmation and instructions
echo "Installation and service setup complete. saycharlie is now running as a service."
echo "You can check the status of the service with 'sudo systemctl status saycharlie.service'"
echo "Access saycharlie Dashboard at: http://saycharlie.local:8337 or http://localhost:8337 or http://$LOCAL_IP:8337"
echo "To stop the service, run 'sudo systemctl stop saycharlie.service'"