from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from routes import dashboard, add_button, set_columns, app_background, settings, category, file_manager, edit_file, \
    delete_file
from threading import Thread
from log_monitor import LogMonitor
from svx_api import process_dtmf_request, start_svxlink_service, restart_svxlink_service


def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app)
    log_monitor = LogMonitor('./logs/svxlink', socketio)

    app.add_url_rule('/files', view_func=file_manager, methods=['GET', 'POST'])
    app.add_url_rule('/files/edit/<filename>', view_func=edit_file, methods=['POST'])
    app.add_url_rule('/files/delete/<filename>', view_func=delete_file, methods=['GET'])

    @app.route('/history')
    def last_talkers():
        talkers = log_monitor.get_last_talkers()
        return render_template('history.html', talkers=talkers, columns=last_talkers)

    @app.route('/send_dtmf/<dtmf_code>', methods=['POST'])
    def send_dtmf_route(dtmf_code):
        success, message = process_dtmf_request(dtmf_code)
        if success:
            return jsonify({"success": True, "message": "DTMF code sent successfully."}), 200
        else:
            return jsonify({"success": False, "message": message}), 500

    @app.route('/start_svxlink', methods=['POST'])
    def start_svxlink_route():
        success, message = start_svxlink_service()
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
        category_name = request.args.get('name')
        return category(category_name)

    # Background thread to monitor logs
    def start_log_monitor():
        log_monitor.start_monitoring()

    thread = Thread(target=start_log_monitor)
    thread.daemon = True
    thread.start()

    return app, socketio


app, socketio = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)  # Use socketio.run to enable WebSocket support
