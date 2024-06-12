#  Copyright (c) 2024 by Silviu Stroe (brainic.io)
#  #
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  #
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#  #
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#  #
#  Created on 5/16/24, 8:44 PM
#  #
#  Author: Silviu Stroe

import configparser
import os
import subprocess
from pathlib import Path
import logging
from flask import request
import socket
import ipaddress
from os import access, R_OK

# Set up logging to file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(module)s - %(levelname)s: %(message)s',
    filename='/tmp/saycharlie.log',
    filemode='a'  # Use 'a' to append to the file
)

path = os.environ.get('PATH')
os.environ['PATH'] = path + ':/bin:/usr/bin'


def send_dtmf_to_svxlink(dtmf_code, dtmf_ctrl_pty):
    try:
        with open(dtmf_ctrl_pty, "w") as f:
            f.write(dtmf_code)
            logging.info(f"DTMF code '{dtmf_code}' sent to svxlink.")
            return True, "Success"
    except IOError as e:
        logging.error(f"Failed to send DTMF code due to IO error: {e}")
        return False, str(e)


def is_svxlink_service_running():
    try:
        result = subprocess.run(["systemctl", "is-active", "svxlink"], text=True, capture_output=True)
        # Check if the service is active without raising an exception for non-zero exit codes
        if result.returncode == 0:
            return True, "SvxLink service is active"
        else:
            return False, "SvxLink service is inactive or does not exist"
    except FileNotFoundError:
        logging.error("systemctl not found, please ensure this script is run on a systemd-based Linux system.")
        return False, "systemctl not found"


def get_log_file_path():
    """
    Attempt to find the SVXLink log file path directly from service properties or fall back to the default location.
    If both fail, execute a shell command to parse the process command-line arguments to determine the log file path.
    """
    # Fall back to the default log file location
    log_file_path = Path("/var/log/svxlink")  # assuming the log file is svxlink.log
    if log_file_path.exists():
        return str(log_file_path), "Log file found at default location."

    # If default location check fails, use the shell command to parse process arguments
    try:
        shell_command = """
        ps aux | grep '[s]vxlink' | grep -- '--logfile' | awk '{
            for (i = 1; i <= NF; i++) {
                split($i, a, "=");
                if (a[1] == "--logfile" && length(a[2]) > 0) print a[2];
            }
        }'
        """
        log_file_via_process = subprocess.check_output(shell_command, shell=True, text=True).strip()
        if log_file_via_process:
            return log_file_via_process, "Log file found using process command-line parsing."

    except subprocess.CalledProcessError as e:
        logging.error("Failed to parse log file path from process arguments: {}".format(e))

    logging.error("Log file not found in service properties, default location, or process arguments.")
    return None, "Log file not found."


def find_config_file():
    """
    Attempt to find the SVXLink configuration file path from service properties or fall back to known locations.
    If both fail, use a shell command to parse process command-line arguments for the configuration file path.
    """

    # Check predefined locations if not found in service properties
    config_locations = [
        Path.home() / ".svxlink" / "svxlink.conf",  # User-specific config
        Path("/etc/svxlink/svxlink.conf"),  # System-wide config
    ]

    for config_path in config_locations:
        try:
            if config_path.exists() and access(config_path, R_OK):
                return str(config_path), "Configuration file found at predefined location."
        except PermissionError as e:
            logging.error(f"Permission denied while accessing {config_path}: {e}")
            continue

    # If predefined locations check fails, use the shell command to parse process arguments
    try:
        shell_command = """
        ps aux | grep '[s]vxlink' | grep -- '--config' | awk '{
            for (i = 1; i <= NF; i++) {
                split($i, a, "=");
                if (a[1] == "--config" && length(a[2]) > 0) print a[2];
            }
        }'
        """
        config_file_via_process = subprocess.check_output(shell_command, shell=True, text=True).strip()
        if config_file_via_process:
            return config_file_via_process, "Configuration file found using process command-line parsing."
    except subprocess.CalledProcessError as e:
        logging.error("Failed to parse configuration file path from process arguments: {}".format(e))

    logging.error(
        "SvxLink configuration file not found in service properties, predefined locations, or process arguments.")
    return None, "SvxLink configuration file not found."


def get_dtmf_ctrl_pty_from_config(config_file):
    config = configparser.ConfigParser(strict=False)
    try:
        config.read(config_file)
        for section in config.sections():
            if config.has_option(section, "DTMF_CTRL_PTY"):
                return config.get(section, "DTMF_CTRL_PTY"), "DTMF control PTY found."
    except configparser.Error as e:
        logging.error(f"Failed to parse configuration file: {e}")
    return None, "DTMF_CTRL_PTY not found in the configuration file."


def get_ptt_ctrl_pty_from_config(config_file):
    config = configparser.ConfigParser(strict=False)
    try:
        config.read(config_file)
        for section in config.sections():
            if config.has_option(section, "PTY_PATH"):
                return config.get(section, "PTY_PATH"), "PTT control PTY found."
    except configparser.Error as e:
        logging.error(f"Failed to parse configuration file: {e}")
    return None, "PTY_PATH not found in the configuration file."


def get_callsign_from_config():
    config_file, message = find_config_file()
    if config_file:
        config = configparser.ConfigParser(strict=False)
        try:
            config.read(config_file)
            for section in config.sections():
                if config.has_option(section, "CALLSIGN"):
                    return config.get(section, "CALLSIGN")
        except configparser.Error as e:
            logging.error(f"Failed to parse configuration file: {e}")
    return None


def process_ptt_request():
    ptt_code = request.get_json().get("ptt_code")
    config_file, message = find_config_file()
    if config_file:
        ptt_ctrl_pty, message = get_ptt_ctrl_pty_from_config(config_file)
        if ptt_ctrl_pty:
            return send_ptt_to_svxlink(ptt_code, ptt_ctrl_pty)
        else:
            return False, message
    return False, message


def send_ptt_to_svxlink(ptt_code, ptt_ctrl_pty):
    try:
        with open(ptt_ctrl_pty, "w") as f:
            f.write(ptt_code)
            logging.info(f"PTT code '{ptt_code}' sent to svxlink.")
            return True, "Success"
    except IOError as e:
        logging.error(f"Failed to send PTT code due to IO error: {e}")
        return False, str(e)


def process_dtmf_request():
    dtmf_code = request.get_json().get("dtmf_code")
    config_file, message = find_config_file()
    if config_file:
        dtmf_ctrl_pty, message = get_dtmf_ctrl_pty_from_config(config_file)
        if dtmf_ctrl_pty:
            return send_dtmf_to_svxlink(dtmf_code, dtmf_ctrl_pty)
        else:
            return False, message
    return False, message


def stop_svxlink_service():
    service_active, message = is_svxlink_service_running()
    if not service_active:
        logging.info("SvxLink service is not running.")
        return True, "SvxLink service is not running."

    try:
        subprocess.run(["systemctl", "stop", "svxlink"], check=True)
        logging.info("SvxLink service stopped successfully.")
        return True, "SvxLink service stopped successfully."
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to stop SvxLink service: {e}")
        return False, str(e)


def restart_svxlink_service():
    try:
        subprocess.run(["systemctl", "restart", "svxlink"], check=True)
        logging.info("SvxLink service restarted successfully.")
        return True, "SvxLink service restarted successfully."
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to restart SvxLink service: {e}")
        return False, str(e)


def get_profile_hosts(profile_path):
    """
    Reads a configuration file and returns the first host specified.
    If the first host is an IP address, returns its hostname.

    Args:
        profile_path (str): Path to the configuration file.

    Returns:
        str: The first host or its resolved hostname, or None if no hosts are found.
    """
    config = configparser.ConfigParser(strict=False)
    try:
        config.read(profile_path)
    except configparser.Error:
        return None

    hosts = [
        host.strip()
        for section in config.sections()
        for option in ["HOSTS", "HOST"]
        if config.has_option(section, option)
        for host in config.get(section, option).split(',')
    ]

    if hosts:
        first_host = hosts[0]
        try:
            # Check if the first host is a valid IP address
            ipaddress.ip_address(first_host)
            try:
                hostname = socket.gethostbyaddr(first_host)[0]
                return hostname
            except socket.herror:
                logging.error(f"Failed to resolve hostname for IP address: {first_host}")
                return first_host
        except ValueError:
            # Not an IP address, return as is
            return first_host

    return None


def get_svx_profiles():
    """
    List all available SVXLink profiles from the /profile-uploads directory and indicate which one is active.
    Each profile is represented as a dictionary with 'name' and 'isActive' properties.
    """

    svx_profiles = []
    svxlink_path = Path('profile-uploads/')
    active_profile, is_symlink = get_active_profile()

    svx_profiles.append({
        'name': active_profile,
        'isActive': True,
        'host': get_profile_hosts(active_profile),
    })

    if svxlink_path.exists():
        for file in svxlink_path.iterdir():
            if file.is_file() and file.suffix == '.conf':
                # profile_name is profile absolute path
                profile_name = str(Path(file).absolute())
                # Append a dictionary with profile name and active status
                if profile_name != active_profile:
                    svx_profiles.append({
                        'name': profile_name,
                        'isActive': False,
                        'host': get_profile_hosts(profile_name),
                    })

    # Sort the profiles by name; active status is not affected by sorting
    svx_profiles.sort(key=lambda x: x['name'])

    return svx_profiles, None


def get_active_profile():
    """
    Determine the currently active svxlink profile by checking which profile the symlink points to.
    """
    config_file, _ = find_config_file()
    if config_file:
        is_sym_link = os.path.islink(config_file)
        # if is symlink, return the target of the symlink
        return os.path.realpath(config_file), is_sym_link
    return None


def switch_svxlink_profile(profile_path):
    """
    Switch the original svxlink configuration file to a symlink pointing to the selected profile.
    """
    try:
        config_file, message = find_config_file()
        if not config_file:
            return False, message

        success, message = backup_original_svxlink_config()
        if not success:
            return False, message

        profile_path = Path(profile_path)
        symlink_path = Path(config_file)

        # Ensure the directory for the symlink exists
        symlink_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove the existing symlink or file if it exists
        if symlink_path.is_symlink() or symlink_path.exists():
            symlink_path.unlink()

        # Create a new symlink
        symlink_path.symlink_to(profile_path)
        logging.info(f"Switched to profile via symlink: {profile_path}")

        # Restart the svxlink service to apply the new configuration
        restart_svxlink_service()

        return True, f"Switched to profile via symlink: {profile_path}"
    except FileNotFoundError as e:
        logging.error(f"Profile configuration file not found: {e}")
        return False, str(e)
    except OSError as e:
        logging.error(f"Failed to switch to profile due to OS error: {e}")
        return False, str(e)
    except Exception as e:  # Catch-all for other unexpected issues
        logging.error(f"An unexpected error occurred: {e}")
        return False, str(e)


def backup_original_svxlink_config():
    """
    Backup the original svxlink configuration file, if no backup exists.
    """
    config_file, message = find_config_file()
    if config_file:
        backup_file = Path(config_file).with_suffix('.bak')
        if not backup_file.exists():
            try:
                Path(config_file).replace(backup_file)
                logging.info(f"Original configuration file backed up to: {backup_file}")
                return True, f"Original configuration file backed up to: {backup_file}"
            except Exception as e:
                logging.error(f"Failed to backup original configuration file: {e}")
                return False, str(e)
        else:
            return True, f"Backup already exists: {backup_file}"
    return False, message


def restore_original_svxlink_config():
    """
    Restore the original svxlink configuration file from the backup
    """
    config_file, message = find_config_file()
    if config_file:
        backup_file = Path(config_file).with_suffix('.bak')
        if backup_file.exists():
            try:
                Path(backup_file).replace(config_file)
                logging.info(f"Original configuration file restored from backup.")

                # Restart the svxlink service to apply the restored configuration
                restart_svxlink_service()

                return True, "Original configuration file restored from backup."
            except Exception as e:
                logging.error(f"Failed to restore original configuration file from backup: {e}")
                return False, str(e)
        else:
            return False, "Backup file does not exist."
    return False, message
