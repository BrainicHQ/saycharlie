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


def get_svx_profiles():
    """
    List all available SVXLink profiles from the /uploads directory and indicate which one is active.
    Each profile is represented as a dictionary with 'name' and 'isActive' properties.
    """
    svx_profiles = []
    svxlink_path = Path('uploads/')
    active_profile = get_active_profile()  # Assumes this function returns the name of the active profile without '.conf'

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
    success, message = backup_original_svxlink_config()
    if not success:
        return False, message

    config_file, message = find_config_file()
    if config_file:
        # Construct the profile_path with a full path starting from the script's current directory
        current_dir = Path(__file__).parent
        profile_path = current_dir / 'uploads' / f'{profile_name}.conf'
        symlink_path = Path(config_file)
        print(symlink_path, symlink_path.is_symlink(), symlink_path.exists())
        print(profile_path, profile_path.is_file(), profile_path.exists())

        try:
            # Ensure the directory for the symlink exists
            symlink_path.parent.mkdir(parents=True, exist_ok=True)

            # Remove the existing symlink or file if it exists
            if symlink_path.is_symlink() or symlink_path.exists():
                symlink_path.unlink()

            # Create a new symlink
            symlink_path.symlink_to(profile_path)
            print(f"Symlink created: {symlink_path} -> {profile_path}")
            logging.info(f"Switched to profile via symlink: {profile_name}")
            return True, f"Switched to profile via symlink: {profile_name}"
        except OSError as e:
            logging.error(f"Failed to switch to profile: {e}")
            return False, str(e)
    else:
        return False, message


def backup_original_svxlink_config():
    """
    Backup the original svxlink configuration file, if no backup exists.
    """
    config_file, message = find_config_file()
    if config_file:
        backup_file = Path(config_file).with_suffix('.bak')
        if not backup_file.exists():  # Check if backup already exists
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
        if backup_file.exists():  # Check if backup file exists
            try:
                Path(backup_file).replace(config_file)
                logging.info(f"Original configuration file restored from backup.")
                return True, "Original configuration file restored from backup."
            except Exception as e:  # Broader exception handling
                logging.error(f"Failed to restore original configuration file from backup: {e}")
                return False, str(e)
        else:
            return False, "Backup file does not exist."
    return False, message
