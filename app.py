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
import logging
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from routes import dashboard, add_button, set_columns, app_background, settings, category, file_manager, edit_file, \
    delete_file, add_talk_group, update_talk_group, delete_talk_group, get_talk_groups_data, get_group_name, \
    get_buttons, system_reboot, system_shutdown, update_app, delete_button, update_button
from threading import Thread, Event
from log_monitor import LogMonitor
from svx_api import process_dtmf_request, stop_svxlink_service, restart_svxlink_service, get_svx_profiles, \
    switch_svxlink_profile, restore_original_svxlink_config, get_log_file_path, process_ptt_request
from zeroconf import ServiceInfo, Zeroconf
import socket
import atexit
from ham_radio_api import HamRadioAPI
from audio import start_audio_monitor
from dateutil import parser

from system_info import get_system_info

# Set up logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(module)s - %(levelname)s: %(message)s',
    filename='/tmp/saycharlie.log',
    filemode='a'  # Use 'a' to append to the file
)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Attempt to connect to an address that requires routing (but does not need to be reachable)
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except socket.error:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def create_app():
    app = Flask(__name__)
    api = HamRadioAPI()
    socketio = SocketIO(app)
    # Get the log file path and the status message
    log_path, message = get_log_file_path()

    try:
        if log_path is None:
            # The log file wasn't found, raise an exception with the message
            raise Exception(message)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        exit(1)

    log_monitor = LogMonitor(log_path, socketio)

    # Get local IP address to advertise
    local_ip = get_local_ip()
    zeroconf = Zeroconf()
    service_info = ServiceInfo(
        "_http._tcp.local.",
        "SVXDashboard._http._tcp.local.",
        addresses=[socket.inet_aton(local_ip)],
        port=8337,
        properties={},
        server="saycharlie.local."
    )

    # Setup for audio monitoring
    stop_audio_monitor = Event()  # This will allow us to stop the thread gracefully
    audio_thread = Thread(target=start_audio_monitor, args=(stop_audio_monitor, socketio))
    audio_thread.daemon = True
    audio_thread.start()

    # Register the service with Zeroconf
    def register_service():
        try:
            zeroconf.register_service(service_info)
            logging.info("Service zeroconf registered")
        except Exception as e:
            logging.info(f"Error registering service zeroconf: {str(e)}")

    # Unregister the service
    def unregister_service():
        zeroconf.unregister_service(service_info)
        zeroconf.close()
        logging.info("Service zeroconf unregistered")

    app.add_url_rule('/files', view_func=file_manager, methods=['GET', 'POST'])
    app.add_url_rule('/files/edit/<filename>', view_func=edit_file, methods=['POST'])
    app.add_url_rule('/files/delete/<filename>', view_func=delete_file, methods=['GET'])

    @app.route('/api/profiles', methods=['GET'])
    def get_svx_profiles_route():
        try:
            profiles, error_message = get_svx_profiles()
            if profiles is not None:
                return jsonify(profiles), 200
            else:
                return jsonify({"error": error_message}), 400  # or another appropriate error status
        except Exception as e:
            # General exception catch to handle unexpected errors gracefully
            return jsonify({"error": str(e)}), 500

    @app.route('/api/switch_profile', methods=['POST'])
    def switch_svxlink_profile_route():
        profile_name = request.json.get('profile')
        success, message = switch_svxlink_profile(profile_name)
        if success:
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"success": False, "message": message}), 500

    @app.route('/api/restore_default_profile', methods=['POST'])
    def restore_default_profile():
        success, message = restore_original_svxlink_config()
        if success:
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"success": False, "message": message}), 500

    @app.route('/api/groups', methods=['GET'])
    def get_talk_groups():
        return get_talk_groups_data()

    @app.route('/api/groups', methods=['POST'])
    def add_talk_group_route():
        return add_talk_group()

    @app.route('/api/groups/<uuid:uuid_id>', methods=['PUT'])
    def update_talk_group_route(uuid_id):
        return update_talk_group(uuid_id)

    @app.route('/api/groups/<uuid:uuid_id>', methods=['DELETE'])
    def delete_talk_group_route(uuid_id):
        return delete_talk_group(uuid_id)

    @app.route('/history')
    def last_talkers():
        talkers = log_monitor.get_last_talkers()

        for talker in talkers:
            if 'stop_date_time' in talker and isinstance(talker['stop_date_time'], str):
                try:
                    # Use dateutil's parser to automatically detect and parse the date
                    parsed_date = parser.parse(talker['stop_date_time'])
                    formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                    talker['stop_date_time'] = formatted_date
                except ValueError:
                    logging.error(f"Error parsing date {talker['stop_date_time']}")
                    talker['stop_date_time'] = 'Invalid date format'  # Fallback value if parsing fails

            details = api.get_ham_details(talker['callsign'])
            talker['name'] = details.get('name', 'Not available')

            # Fill tg_name based on talkgroup number found in the settings
            talker['tg_name'] = get_group_name(talker['tg_number'])

        return render_template('history.html', talkers=talkers)

    @socketio.on('connect')
    def handle_connect():
        # Send the last active talker to the client on connect
        current_talker = log_monitor.get_active_talker()
        past_talkers = log_monitor.get_last_talkers()
        if current_talker:
            emit('update_last_talker', current_talker)  # Send the active talker
        elif past_talkers:
            emit('update_last_talker', past_talkers[0])  # Send the most recent talker

    @app.route('/api/send_dtmf', methods=['POST'])
    def send_dtmf_route():
        success, message = process_dtmf_request()
        if success:
            return jsonify({"success": True, "message": "DTMF code sent successfully."}), 200
        else:
            return jsonify({"success": False, "message": message}), 500

    @app.route('/api/send_ptt', methods=['POST'])
    def send_ptt_route():
        success, message = process_ptt_request()
        if success:
            return jsonify({"success": True, "message": "PTT code sent successfully."}), 200
        else:
            return jsonify({"success": False, "message": message}), 500

    @app.route('/stop_svxlink', methods=['POST'])
    def stop_svxlink_route():
        success, message = stop_svxlink_service()
        if success:
            return jsonify({"success": True, "message": "SvxLink service stopped successfully."}), 200
        else:
            return jsonify({"success": False, "message": message}), 500

    @app.route('/restart_svxlink', methods=['POST'])
    def restart_svxlink_route():
        success, message = restart_svxlink_service()
        if success:
            return jsonify({"success": True, "message": "SvxLink service restarted successfully."}), 200
        else:
            return jsonify({"success": False, "message": message}), 500

    @app.route('/api/get-name/<callsign>', methods=['GET'])
    def get_name_from_callsign_route(callsign):
        details = api.get_ham_details(callsign)
        if 'error' in details:
            return jsonify({"error": details['error']}), 400
        return jsonify({"name": details.get('name', 'Not available')}), 200

    @app.route('/api/get-group-name/<tg_number>', methods=['GET'])
    def get_group_name_route(tg_number):
        name = get_group_name(tg_number)
        if name is None:
            return jsonify({"error": "Talkgroup not found"}), 404
        return jsonify({"name": name}), 200

    @app.route('/api/system_reboot', methods=['POST'])
    def system_reboot_route():
        return system_reboot()

    @app.route('/api/system_shutdown', methods=['POST'])
    def system_shutdown_route():
        return system_shutdown()

    @app.route('/api/update_app', methods=['POST'])
    def update_app_route():
        return update_app()

    @app.route('/api/system-info', methods=['GET'])
    def get_system_info_route():
        return jsonify(get_system_info()), 200

    # Define routes
    @app.route('/')
    def index():
        return dashboard()

    @app.route('/api/buttons', methods=['POST'])
    def add_button_route():
        return add_button()

    @app.route('/api/buttons', methods=['GET'])
    def get_buttons_route():
        return get_buttons()

    @app.route('/api/buttons/<uuid:uuid_id>', methods=['PUT'])
    def update_button_route(uuid_id):
        return update_button(uuid_id)

    @app.route('/api/buttons/<uuid:uuid_id>', methods=['DELETE'])
    def delete_button_route(uuid_id):
        return delete_button(uuid_id)

    @app.route('/set_columns', methods=['POST'])
    def set_columns_route():
        return set_columns()

    @app.route('/app_background', methods=['POST'])
    def app_background_route():
        return app_background()

    @app.route('/settings', methods=['GET'])
    def settings_route():
        return settings()

    @app.route('/category', methods=['GET'])
    def category_route():
        category_uuid = request.args.get('id')
        return category(category_uuid)

    # Background thread to monitor logs
    def start_log_monitor():
        log_monitor.start_monitoring()

    thread = Thread(target=start_log_monitor)
    thread.daemon = True
    thread.start()

    atexit.register(unregister_service)
    register_service()  # Register the service with Zeroconf
    return app, socketio, register_service


app, socketio, register_service = create_app()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8337, debug=False)
