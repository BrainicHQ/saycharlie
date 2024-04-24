from flask import Flask, request
from routes import dashboard, add_button, set_columns, app_background, settings, category

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


@app.route('/category', methods=['GET'])
def category_route():
    category_name = request.args.get('name')
    return category(category_name)


if __name__ == '__main__':
    app.run(debug=True)
