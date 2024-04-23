import os
import json


def load_settings():
    initial_data = {'buttons': [{'label': 'Button 1', 'action': '#', 'color': '#4CAF50'},
                                {'label': 'Button 2', 'action': '#', 'color': '#2196F3'}],
                    'columns': 2,
                    'app_background': '#f0f0f0'}

    if os.path.exists('config.json') and os.path.getsize('config.json') > 0:
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except json.decoder.JSONDecodeError:
            print("Error: Config file is empty or invalid JSON. Using default initial data.")
            return initial_data
    else:
        return initial_data


def save_settings(settings_data):
    with open('config.json', 'w') as f:
        json.dump(settings_data, f, indent=4)
