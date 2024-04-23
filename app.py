from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)

# Check if config file exists, if not, create it with initial structure and default buttons
if not os.path.exists('config.json'):
    initial_data = {'buttons': [{'label': 'Button 1', 'action': '#', 'color': '#4CAF50'},
                                {'label': 'Button 2', 'action': '#', 'color': '#2196F3'}],
                    'columns': 2}
    with open('config.json', 'w') as f:
        json.dump(initial_data, f)

# Load initial settings from config file
with open('config.json', 'r') as f:
    settings_data = json.load(f)

# Check if 'buttons' key exists and is not empty, if not, add default buttons
if 'buttons' not in settings_data or not settings_data['buttons']:
    settings_data['buttons'] = [{'label': 'Button 1', 'action': '#', 'color': '#4CAF50'},
                                {'label': 'Button 2', 'action': '#', 'color': '#2196F3'}]

# Check if 'columns' key exists and is not empty, if not, set a default value
if 'columns' not in settings_data:
    settings_data['columns'] = 2


@app.route('/')
def dashboard():
    return render_template('dashboard.html', buttons=settings_data['buttons'], columns=settings_data['columns'])


@app.route('/add_button', methods=['POST'])
def add_button():
    if request.method == 'POST':
        # Process form submission and update button settings
        new_button = {
            'label': request.form['label'],
            'action': request.form['action'],
            'color': request.form['color']
        }
        settings_data['buttons'].append(new_button)

        # Save updated settings to config file
        with open('config.json', 'w') as f:
            json.dump(settings_data, f, indent=4)

        return redirect('/')


@app.route('/set_columns', methods=['POST'])
def set_columns():
    if request.method == 'POST':
        # Process form submission and update the number of columns
        columns = int(request.form['columns'])
        settings_data['columns'] = columns

        # Save updated settings to config file
        with open('config.json', 'w') as f:
            json.dump(settings_data, f, indent=4)

        return redirect('/')


@app.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html', columns=settings_data['columns'])


if __name__ == '__main__':
    app.run(debug=True)

