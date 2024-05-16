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

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from routes import dashboard, add_button, set_columns, app_background, settings, category, file_manager, edit_file, \
    delete_file, add_talk_group, update_talk_group, delete_talk_group, get_talk_groups_data, get_group_name
from threading import Thread
from log_monitor import LogMonitor
from svx_api import process_dtmf_request, stop_svxlink_service, restart_svxlink_service, get_svx_profiles, \
    switch_svxlink_profile, restore_original_svxlink_config, get_log_file_path
from zeroconf import ServiceInfo, Zeroconf
import socket
import atexit
from ham_radio_api import HamRadioAPI


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
    log_path = 'logs/svxlink'  # get_log_file_path()
    try:
        if log_path is None:
            raise Exception("Log file not found.")
    except Exception as e:
        print(f"Error: {str(e)}")
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

    # Register the service with Zeroconf
    def register_service():
        try:
            zeroconf.register_service(service_info)
            print("Service registered")
        except Exception as e:
            print(f"Error registering service: {str(e)}")

    # Unregister the service
    def unregister_service():
        zeroconf.unregister_service(service_info)
        zeroconf.close()
        print("Service unregistered")

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
            details = api.get_ham_details(talker['callsign'])
            talker['name'] = details.get('name', 'Not available')
            # fill tg_name based on talkgroup number found in the settings
            talker['tg_name'] = get_group_name(talker['tg_number'])
        return render_template('history.html', talkers=talkers, columns=last_talkers)

    @socketio.on('connect')
    def handle_connect():
        # get last talker
        current_talkers = log_monitor.get_last_talkers()
        if current_talkers:
            emit('update_last_talker', current_talkers[0])

    @app.route('/api/send_dtmf', methods=['POST'])
    def send_dtmf_route():
        success, message = process_dtmf_request()
        if success:
            return jsonify({"success": True, "message": "DTMF code sent successfully."}), 200
        else:
            return jsonify({"success": False, "message": message}), 500

    @app.route('/stop_svxlink', methods=['POST'])
    def stop_svxlink_route():
        success, message = stop_svxlink_service()
        if success:
            return jsonify({"success": True, "message": "SvxLink service started successfully."}), 200
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

    # Define routes
    @app.route('/')
    def index():
        return dashboard()

    @app.route('/add_button', methods=['POST'])
    def add_button_route():
        return add_button()

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

    return app, socketio, register_service


app, socketio, register_service = create_app()

if __name__ == '__main__':
    register_service()  # Register the service with Zeroconf
    socketio.run(app, host='0.0.0.0', port=8337, debug=True)
