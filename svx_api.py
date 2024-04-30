import configparser
import re
import subprocess
import sys
from pathlib import Path
import logging
from flask import request

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def system_check():
    if not sys.platform.startswith('linux'):
        error_msg = "Unsupported operating system for this script."
        logging.error(error_msg)
        return False, error_msg  # Indicate failure and provide an error message for the API
    return True


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
        output = subprocess.check_output(["systemctl", "is-active", "svxlink"], universal_newlines=True)
        return output.strip() == "active", "SvxLink service is active"
    except FileNotFoundError:
        logging.error("systemctl not found, please ensure this script is run on a systemd-based Linux system.")
        return False, "systemctl not found"


def find_config_file():
    user_config_path = Path.home() / ".svxlink" / "svxlink.conf"
    if user_config_path.exists():
        return str(user_config_path), "User-specific configuration found."
    system_config_path = Path("/etc/svxlink/svxlink.conf")
    if system_config_path.exists():
        return str(system_config_path), "System-wide configuration found."

    service_active, message = is_svxlink_service_running()
    if service_active:
        try:
            exec_start_output = subprocess.check_output(["systemctl", "show", "--property=ExecStart", "svxlink"],
                                                        universal_newlines=True)
            config_file_match = re.search(r'--config=(\S+)', exec_start_output)
            if config_file_match:
                return config_file_match.group(1), "Config file found in service properties."
            logging.error("No config file specified in service properties.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error while trying to retrieve configuration from service: {e}")
        return None, "Failed to locate configuration file."
    return None, "SvxLink configuration file not found."


def get_dtmf_ctrl_pty_from_config(config_file):
    config = configparser.ConfigParser()
    try:
        config.read(config_file)
        for section in config.sections():
            if config.has_option(section, "DTMF_CTRL_PTY"):
                return config.get(section, "DTMF_CTRL_PTY"), "DTMF control PTY found."
    except configparser.Error as e:
        logging.error(f"Failed to parse configuration file: {e}")
    return None, "DTMF_CTRL_PTY not found in the configuration file."


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


def start_svxlink_service():
    system_compatible, system_message = system_check()  # Check system compatibility
    if not system_compatible:
        return False, system_message  # Return error message for the API

    service_active, message = is_svxlink_service_running()
    if service_active:
        logging.info("SvxLink service is already running.")
        return False, "SvxLink service is already running."

    try:
        subprocess.run(["systemctl", "start", "svxlink"], check=True)
        logging.info("SvxLink service started successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start SvxLink service: {e}")
        return False, str(e)


def restart_svxlink_service():
    system_compatible, system_message = system_check()  # Check system compatibility
    if not system_compatible:
        return False, system_message  # Return error message for the API

    try:
        subprocess.run(["systemctl", "restart", "svxlink"], check=True)
        logging.info("SvxLink service restarted successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to restart SvxLink service: {e}")
        return False, str(e)
