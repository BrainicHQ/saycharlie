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
        return False
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


def get_log_file_path():
    """
    Attempt to find the SVXLink log file path directly from service properties or fall back to the default location.
    """
    try:
        exec_start_output = subprocess.check_output(
            ["systemctl", "show", "--property=ExecStart", "svxlink"], universal_newlines=True
        )
        log_file_match = re.search(r'--logfile=(\S+)', exec_start_output)
        if log_file_match:
            return log_file_match.group(1), "Log file found in service properties."
    except subprocess.CalledProcessError as e:
        logging.error(f"Error retrieving log file from service: {e}")

    log_file_path = Path("/var/log/svxlink/svxlink.log")
    if log_file_path.exists():
        return str(log_file_path), "Log file found at default location."

    logging.error("Log file not found in service properties or default location.")
    return None, "Log file not found."


def find_config_file():
    """
    Attempt to find the SVXLink configuration file path from service properties or fall back to known locations.
    """
    # system check using the system_check function
    system_compatible = system_check()
    if not system_compatible:
        return None, "Unsupported system."

    try:
        exec_start_output = subprocess.check_output(
            ["systemctl", "show", "--property=ExecStart", "svxlink"], universal_newlines=True
        )
        config_file_match = re.search(r'--config=(\S+)', exec_start_output)
        if config_file_match:
            return config_file_match.group(1), "Configuration file found in service properties."
    except subprocess.CalledProcessError as e:
        logging.error(f"Error retrieving configuration from service: {e}")

    # Check predefined locations if not found in service properties
    config_locations = [
        Path.home() / ".svxlink" / "svxlink.conf",  # User-specific config
        Path("/etc/svxlink/svxlink.conf"),  # System-wide config
    ]

    for config_path in config_locations:
        if config_path.exists():
            return str(config_path), "Configuration file found at predefined location."

    logging.error("SvxLink configuration file not found in service properties or predefined locations.")
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


def stop_svxlink_service():
    system_compatible = system_check()  # Check system compatibility
    if not system_compatible:
        return False, "Unsupported system."

    service_active, message = is_svxlink_service_running()
    if not service_active:
        logging.info("SvxLink service is not running.")
        return True, "SvxLink service is not running."

    try:
        subprocess.run(["systemctl", "stop", "svxlink"], check=True)
        logging.info("SvxLink service stopped successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to stop SvxLink service: {e}")
        return False, str(e)


def restart_svxlink_service():
    system_compatible = system_check()  # Check system compatibility
    if not system_compatible:
        return False, "Unsupported system."

    try:
        subprocess.run(["systemctl", "restart", "svxlink"], check=True)
        logging.info("SvxLink service restarted successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to restart SvxLink service: {e}")
        return False, str(e)


def get_svx_profiles():
    """
    List all available SVXLink profiles from the /profile-uploads directory and indicate which one is active.
    Each profile is represented as a dictionary with 'name' and 'isActive' properties.
    """
    # system check using the system_check function
    system_compatible = system_check()
    if not system_compatible:
        return None, "Unsupported system."

    svx_profiles = []
    svxlink_path = Path('profile-uploads/')
    active_profile = get_active_profile()

    if svxlink_path.exists():
        for file in svxlink_path.iterdir():
            if file.is_file() and file.suffix == '.conf':
                profile_name = file.stem
                # Append a dictionary with the profile name and its active status
                svx_profiles.append({
                    'name': profile_name,
                    'isActive': (profile_name == active_profile)
                })

    # Sort the profiles by name; active status is not affected by sorting
    svx_profiles.sort(key=lambda x: x['name'])

    return svx_profiles


def get_active_profile():
    """
    Determine the currently active svxlink profile by checking which profile the symlink points to.
    """
    config_file, _ = find_config_file()
    if config_file and Path(config_file).is_symlink():
        return Path(config_file).resolve().stem
    return None


def switch_svxlink_profile(profile_name):
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

        current_dir = Path(__file__).parent
        profile_path = current_dir / 'profile-uploads' / f'{profile_name}.conf'
        symlink_path = Path(config_file)

        # Ensure the directory for the symlink exists
        symlink_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove the existing symlink or file if it exists
        if symlink_path.is_symlink() or symlink_path.exists():
            symlink_path.unlink()

        # Create a new symlink
        symlink_path.symlink_to(profile_path)
        logging.info(f"Switched to profile via symlink: {profile_name}")
        return True, f"Switched to profile via symlink: {profile_name}"
    except OSError as e:
        logging.error(f"Failed to switch to profile due to OS error: {e}")
        return False, str(e)
    except FileNotFoundError as e:
        logging.error(f"Profile configuration file not found: {e}")
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
                return True, "Original configuration file restored from backup."
            except Exception as e:
                logging.error(f"Failed to restore original configuration file from backup: {e}")
                return False, str(e)
        else:
            return False, "Backup file does not exist."
    return False, message
