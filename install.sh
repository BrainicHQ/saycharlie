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

# Directory of the script
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check for root privileges
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "Starting the installation of the saycharlie SVX Dashboard..."

install_python_packages() {
    # Install Python 3, pip, and python3-venv if they are not already installed
    if command -v apt-get &>/dev/null; then
        apt-get update
        apt-get install -y python3 python3-pip python3-venv python3-dev || { echo "apt-get command failed"; exit 1; }
    elif command -v dnf &>/dev/null; then
        dnf install -y python3 python3-pip python3-venv python3-devel || { echo "dnf command failed"; exit 1; }
    elif command -v pacman &>/dev/null; then
        pacman -Sy --noconfirm python python-pip python-virtualenv base-devel || { echo "pacman command failed"; exit 1; }
    elif command -v yum &>/dev/null; then
        yum install -y python3 python3-pip python3-venv python3-devel || { echo "yum command failed"; exit 1; }
    elif command -v zypper &>/dev/null; then
        zypper install -y python3 python3-pip python3-venv python3-devel || { echo "zypper command failed"; exit 1; }
    else
        echo "Unsupported package manager. Please install Python packages manually."
        exit 1
    fi
}

create_virtual_environment() {
    echo "Creating a virtual environment..."
    python3 -m venv "$APP_DIR/venv" || { echo "Failed to create virtual environment"; exit 1; }
    echo "Virtual environment created."

    . "$APP_DIR/venv/bin/activate" || { echo "Failed to activate virtual environment"; exit 1; }

    # Update pip to the latest version
    echo "Updating pip to the latest version..."
    python3 -m pip install --upgrade pip || { echo "Failed to upgrade pip"; exit 1; }
}

install_dependencies() {
    if [ ! -f "$APP_DIR/requirements.txt" ]; then
        echo "requirements.txt file does not exist in the same directory as the script."
        exit 1
    fi

    echo "Installing dependencies from requirements.txt..."
    pip install -r "$APP_DIR/requirements.txt" || { echo "Failed to install dependencies"; exit 1; }
    echo "Dependencies installed."
}

setup_systemd_service() {
    # Determine the owner of the svxlink binary
    SVXLINK_PROCESS_USER=$(ps aux | grep '[s]vxlink' | awk '{print $1}')

    if [ -z "$SVXLINK_PROCESS_USER" ]; then
        echo "No active svxlink process found, defaulting to user 'svxlink'."
        SVXLINK_PROCESS_USER="svxlink"
    else
        echo "svxlink is running under user: $SVXLINK_PROCESS_USER"
    fi

    if [ ! -f "$APP_DIR/app.py" ]; then
        echo "app.py file does not exist in the same directory as the script."
        exit 1
    fi

    SERVICE_FILE=/etc/systemd/system/saycharlie.service
    echo "Creating a systemd service file at $SERVICE_FILE"

    cat << EOF | tee $SERVICE_FILE > /dev/null
[Unit]
Description=saycharlie SVX Dashboard
After=network.target

[Service]
User=$SVXLINK_PROCESS_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="FLASK_APP=app.py"
ExecStart=$APP_DIR/venv/bin/flask run --host=0.0.0.0 --port=8337

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable saycharlie.service
    systemctl start saycharlie.service
}

provide_feedback() {
       LOCAL_IP=$(hostname -I | cut -d' ' -f1 || { echo "Failed to retrieve local IP address"; exit 1; })

    if systemctl is-active --quiet saycharlie.service; then
        echo "saycharlie service has been started and enabled at boot."
        echo "Installation and service setup complete. saycharlie is now running as a service."
        echo "You can check the status of the service with 'systemctl status saycharlie.service'"
        echo "Access saycharlie Dashboard at:"
        echo "http://saycharlie.local:8337"  # Only works if mDNS is configured
        echo "http://localhost:8337"
        echo "http://${LOCAL_IP}:8337"
        # try to open the browser to the dashboard universally on all systems
        echo "Attempting to open the saycharlie Dashboard in your default browser..."
        if command -v xdg-open &>/dev/null; then
            xdg-open "http://localhost:8337" || { echo "Failed to open the browser"; }
        elif command -v open &>/dev/null; then
            open "http://localhost:8337" || { echo "Failed to open the browser"; }
        elif command -v start &>/dev/null; then
            start "http://localhost:8337" || { echo "Failed to open the browser"; }
        fi

    else
        echo "Failed to start saycharlie service. Please check the service status or journal logs for details."
        echo "Run 'systemctl status saycharlie.service' or 'journalctl -xe' for more information."
        exit 1
    fi

    echo "To stop the service, run 'systemctl stop saycharlie.service'"
}

# Function Calls
install_python_packages
create_virtual_environment
install_dependencies
setup_systemd_service
provide_feedback