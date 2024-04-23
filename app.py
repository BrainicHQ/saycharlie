from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)

# Initialize settings_data with default data
initial_data = {'buttons': [{'label': 'Button 1', 'action': '#', 'color': '#4CAF50'},
                            {'label': 'Button 2', 'action': '#', 'color': '#2196F3'}],
                'columns': 2}

# Check if config file exists and is non-empty
if os.path.exists('config.json') and os.path.getsize('config.json') > 0:
    try:
        # Load initial settings from config file
        with open('config.json', 'r') as f:
            settings_data = json.load(f)
    except json.decoder.JSONDecodeError:
        # Handle the case when the JSON file is empty or invalid
        print("Error: Config file is empty or invalid JSON. Using default initial data.")
        settings_data = initial_data
else:
    # Use default initial data if config file doesn't exist or is empty
    settings_data = initial_data

# Check if 'buttons' key exists and is not empty, if not, add default buttons
if 'buttons' not in settings_data or not settings_data['buttons']:
    settings_data['buttons'] = initial_data['buttons']

# Check if 'columns' key exists and is not empty, if not, set a default value
if 'columns' not in settings_data:
    settings_data['columns'] = initial_data['columns']

# Check if 'app_background' key exists and is not empty, if not, set a default value
if 'app_background' not in settings_data:
    settings_data['app_background'] = '#f0f0f0'


@app.route('/')
def dashboard():
    return render_template('dashboard.html', buttons=settings_data['buttons'],
                           columns=settings_data['columns'], app_background=settings_data['app_background'])


@app.route('/add_button', methods=['POST'])
def add_button():
    if request.method == 'POST':
        # Process form submission and update button settings
        new_button = {
            'label': request.form['label'],
            'color': request.form['color'],
            'category': request.form.get('category'),  # Get the category if provided
            'isCategory': 'parent_category' in request.form  # Check if it's a parent category
        }

        # If it's a parent category, disable the action field
        if new_button['isCategory']:
            new_button['action'] = ''
            # Add it as a parent category
            new_category = {
                'label': new_button['label'],
                'buttons': []
            }
            settings_data.setdefault('categories', []).append(new_category)
        else:
            new_button['action'] = request.form['action']  # Get the action if not a parent category

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


@app.route('/app_background', methods=['POST'])
def app_background():
    if request.method == 'POST':
        # Process form submission and update the app background
        app_background = request.form['app_background']
        settings_data['app_background'] = app_background

        # Save updated settings to config file
        with open('config.json', 'w') as f:
            json.dump(settings_data, f, indent=4)

        return redirect('/')


@app.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html', columns=settings_data['columns'], buttons=settings_data['buttons'])


if __name__ == '__main__':
    app.run(debug=True)
