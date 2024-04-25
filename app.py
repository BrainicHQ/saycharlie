from flask import Flask, request
from flask_socketio import SocketIO, emit
from routes import dashboard, add_button, set_columns, app_background, settings, category
from threading import Thread
from log_monitor import LogMonitor


def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app)
    log_monitor = LogMonitor('./logs/svxlink', socketio)

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
