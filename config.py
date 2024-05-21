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

import os
import json


def load_settings():
    config_path = 'config.json'
    initial_data = {
        'buttons': [],
        'columns': 2,
        'app_background': '#f0f0f0'
    }

    # Check if the config file exists
    if os.path.exists(config_path):
        # Check if the file is non-empty
        if os.path.getsize(config_path) > 0:
            try:
                with open(config_path, 'r') as file:
                    data = json.load(file)
                print("Config loaded successfully.")
                return data
            except json.decoder.JSONDecodeError:
                print("Error: Config file is invalid JSON. Using default settings.")
        else:
            print("Error: Config file is empty. Using default settings.")
    else:
        # Create a new config file with initial data if it doesn't exist
        with open(config_path, 'w') as file:
            json.dump(initial_data, file, indent=4)
        print("Config file created with initial data.")

    # Return default settings if no valid config was loaded
    return initial_data


def save_settings(settings_data):
    with open('config.json', 'w') as f:
        json.dump(settings_data, f, indent=4)
