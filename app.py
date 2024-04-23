from flask import Flask
from routes import dashboard, add_button, set_columns, app_background, settings

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(debug=True)
