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

###############################################################################
# Calculate the default application directory from where this script is run.
###############################################################################
DEFAULT_APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
APP_DIR="${DEFAULT_APP_DIR}"

###############################################################################
# Function: detect_svxlink_user
# Detect the user running the "svxlink" process.
###############################################################################
detect_svxlink_user() {
    local user
    user=$(ps -eo user,comm | awk '$2=="svxlink" { print $1; exit }')
    if [ -z "$user" ]; then
        echo "No active svxlink process found, defaulting to 'svxlink'."
        user="svxlink"
    else
        echo "Detected svxlink process user: $user"
    fi
    echo "$user"
}

# Set default variables that depend on APP_DIR
VENV_DIR="${APP_DIR}/venv"
APP_FILE="${APP_DIR}/app.py"
SERVICE_FILE="/etc/systemd/system/saycharlie.service"
FLASK_HOST="0.0.0.0"
FLASK_PORT="8337"
SVXLINK_USER="$(detect_svxlink_user)"
SUDOERS_FILE="/etc/sudoers.d/svxlink"

###############################################################################
# Function: configure_parameters
# Display default parameters and allow the user to modify them.
###############################################################################
configure_parameters() {
    echo "=============================================="
    echo "Detected installation parameters:"
    echo "1. Application Directory (APP_DIR)        : ${APP_DIR}"
    echo "2. Virtual Environment Directory (VENV_DIR) : ${VENV_DIR}"
    echo "3. saycharlie Application File (APP_FILE)        : ${APP_FILE}"
    echo "4. Systemd Service File (SERVICE_FILE)        : ${SERVICE_FILE}"
    echo "5. saycharlie Host (FLASK_HOST)                    : ${FLASK_HOST}"
    echo "6. saycharlie Port (FLASK_PORT)                    : ${FLASK_PORT}"
    echo "7. SVXLINK Process User (SVXLINK_USER)        : ${SVXLINK_USER}"
    echo "8. Sudoers File (SUDOERS_FILE)                : ${SUDOERS_FILE}"
    echo "=============================================="

    read -rp "Would you like to modify any parameters? (Y/n): " modify_choice
    modify_choice=${modify_choice:-N}
    if [[ "$modify_choice" =~ ^[Yy]$ ]]; then
        read -rp "Enter saycharlie Application Directory (APP_DIR) [${APP_DIR}]: " input
        APP_DIR=${input:-$APP_DIR}
        # Recalculate dependent paths based on new APP_DIR:
        VENV_DIR="${APP_DIR}/venv"
        APP_FILE="${APP_DIR}/app.py"

        read -rp "Enter saycharlie Virtual Environment Directory (VENV_DIR) [${VENV_DIR}]: " input
        VENV_DIR=${input:-$VENV_DIR}

        read -rp "Enter saycharlie Application File (APP_FILE) [${APP_FILE}]: " input
        APP_FILE=${input:-$APP_FILE}

        read -rp "Enter Systemd Service File (SERVICE_FILE) [${SERVICE_FILE}]: " input
        SERVICE_FILE=${input:-$SERVICE_FILE}

        read -rp "Enter saycharlie Host (FLASK_HOST) [${FLASK_HOST}]: " input
        FLASK_HOST=${input:-$FLASK_HOST}

        read -rp "Enter saycharlie Port (FLASK_PORT) [${FLASK_PORT}]: " input
        FLASK_PORT=${input:-$FLASK_PORT}

        read -rp "Enter SVXLINK Process User (SVXLINK_USER) [${SVXLINK_USER}]: " input
        SVXLINK_USER=${input:-$SVXLINK_USER}

        read -rp "Enter Sudoers File (SUDOERS_FILE) [${SUDOERS_FILE}]: " input
        SUDOERS_FILE=${input:-$SUDOERS_FILE}
    fi

    echo "=============================================="
    echo "Final installation parameters:"
    echo "Application Directory (APP_DIR)        : ${APP_DIR}"
    echo "Virtual Environment Directory (VENV_DIR) : ${VENV_DIR}"
    echo "saycharlie Application File (APP_FILE)        : ${APP_FILE}"
    echo "Systemd Service File (SERVICE_FILE)        : ${SERVICE_FILE}"
    echo "saycharlie Host (FLASK_HOST)                    : ${FLASK_HOST}"
    echo "saycharlie Port (FLASK_PORT)                    : ${FLASK_PORT}"
    echo "SVXLINK Process User (SVXLINK_USER)        : ${SVXLINK_USER}"
    echo "Sudoers File (SUDOERS_FILE)                : ${SUDOERS_FILE}"
    echo "=============================================="

    read -rp "Confirm these parameters? (Y/n): " confirm
    confirm=${confirm:-Y}
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Installation aborted by user."
        exit 1
    fi

    # Validate that the specified SVXLINK_USER exists.
    while ! id "$SVXLINK_USER" &>/dev/null; do
        echo "Error: The user '$SVXLINK_USER' does not exist."
        read -rp "Please enter an existing user for SVXLINK (or type 'exit' to abort): " input
        if [[ "$input" =~ ^[Ee]xit$ ]]; then
            echo "Installation aborted by user."
            exit 1
        fi
        SVXLINK_USER=${input}
    done
}

###############################################################################
# Function: install_python_packages
# Install Python and related packages using the appropriate package manager.
###############################################################################
install_python_packages() {
    echo "Installing required system packages for Python..."
    if command -v apt-get &>/dev/null; then
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq
        apt-get install -y python3 python3-pip python3-venv python3-dev libopenblas-dev
    elif command -v dnf &>/dev/null; then
        dnf install -y python3 python3-pip python3-venv python3-devel openblas-devel
    elif command -v pacman &>/dev/null; then
        pacman -Sy --noconfirm python python-pip python-virtualenv base-devel openblas
    elif command -v yum &>/dev/null; then
        yum install -y python3 python3-pip python3-venv python3-devel openblas-devel
    elif command -v zypper &>/dev/null; then
        zypper install -y python3 python3-pip python3-venv python3-devel openblas-devel
    else
        echo "Unsupported package manager. Please install the required packages manually." >&2
        exit 1
    fi
    echo "System packages installed."
}

###############################################################################
# Function: create_virtual_environment
# Create and activate a Python virtual environment.
###############################################################################
create_virtual_environment() {
    echo "Creating virtual environment in ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
    echo "Activating virtual environment..."
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
    echo "Upgrading pip..."
    pip install --upgrade pip
}

###############################################################################
# Function: install_dependencies
# Install the Flask application dependencies.
###############################################################################
install_dependencies() {
    if [ ! -f "${APP_DIR}/requirements.txt" ]; then
        echo "Error: requirements.txt not found in ${APP_DIR}. Aborting installation." >&2
        exit 1
    fi
    echo "Installing Python dependencies..."
    pip install -r "${APP_DIR}/requirements.txt"
}

###############################################################################
# Function: setup_systemd_service
# Create a systemd service file for the Flask application.
###############################################################################
setup_systemd_service() {
    if [ ! -f "${APP_FILE}" ]; then
        echo "Error: ${APP_FILE} not found. Aborting installation." >&2
        exit 1
    fi

    echo "Creating systemd service file at ${SERVICE_FILE}..."
    cat <<EOF > "${SERVICE_FILE}"
[Unit]
Description=saycharlie SVX Dashboard
After=network.target

[Service]
User=${SVXLINK_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
Environment="FLASK_APP=$(basename "${APP_FILE}")"
ExecStart=${VENV_DIR}/bin/flask run --host=${FLASK_HOST} --port=${FLASK_PORT}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    echo "Reloading systemd daemon and enabling service..."
    systemctl daemon-reload
    systemctl enable "$(basename "${SERVICE_FILE}")"
    systemctl start "$(basename "${SERVICE_FILE}")"
}

###############################################################################
# Function: setup_sudoers
# Configure a sudoers file for passwordless execution of specific commands.
###############################################################################
setup_sudoers() {
    echo "Setting up sudoers for user '${SVXLINK_USER}'..."
    cat <<EOF > "${SUDOERS_FILE}"
${SVXLINK_USER} ALL=(ALL) NOPASSWD: /bin/systemctl stop svxlink, /bin/systemctl start svxlink, /bin/systemctl restart svxlink, /sbin/shutdown, /sbin/reboot, /usr/bin/git *
EOF
    chmod 0440 "${SUDOERS_FILE}"
    echo "Sudoers configuration applied at ${SUDOERS_FILE}."
}

###############################################################################
# Function: provide_feedback
# Provide final feedback and attempt to open the dashboard in a browser.
###############################################################################
provide_feedback() {
    local LOCAL_IP
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    if systemctl is-active --quiet "$(basename "${SERVICE_FILE}")"; then
        echo "saycharlie service is active and enabled at boot."
        echo "Access the Dashboard at:"
        echo "  • http://saycharlie.local:${FLASK_PORT} (if mDNS is configured)"
        echo "  • http://localhost:${FLASK_PORT}"
        echo "  • http://${LOCAL_IP}:${FLASK_PORT}"
        echo "Attempting to open the dashboard in your default browser..."
        if command -v xdg-open &>/dev/null; then
            xdg-open "http://localhost:${FLASK_PORT}" || echo "Warning: xdg-open failed."
        elif command -v open &>/dev/null; then
            open "http://localhost:${FLASK_PORT}" || echo "Warning: open command failed."
        else
            echo "No supported command found to open a browser automatically."
        fi
    else
        echo "Error: saycharlie service failed to start. Check its status with 'systemctl status $(basename "${SERVICE_FILE}")' or view logs with 'journalctl -xe'." >&2
        exit 1
    fi

    echo "To stop the service, run: systemctl stop $(basename "${SERVICE_FILE}")"
}

###############################################################################
# Main function: orchestrates the installation steps.
###############################################################################
main() {
    # Interactively confirm or modify installation parameters.
    configure_parameters

    install_python_packages
    create_virtual_environment
    install_dependencies
    setup_systemd_service

    read -rp "Do you want to configure passwordless sudo for user '${SVXLINK_USER}'? (Y/n): " sudoers_choice
    sudoers_choice=${sudoers_choice:-Y}
    if [[ "$sudoers_choice" =~ ^[Yy]$ ]]; then
        setup_sudoers
    fi

    provide_feedback
}

# Check for root privileges.
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root." >&2
    exit 1
fi

echo "Starting the installation of the saycharlie SVX Dashboard..."
echo "Powered by Silviu Stroe - YO6SAY"
main "$@"