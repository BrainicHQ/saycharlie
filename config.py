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
    initial_data = {'buttons': [],
                    'columns': 2,
                    'app_background': '#f0f0f0'}

    if os.path.exists('config.json'):
        if os.path.getsize('config.json') > 0:
            try:
                with open('config.json', 'r') as f:
                    return json.load(f)
            except json.decoder.JSONDecodeError:
                print("Error: Config file is empty or invalid JSON. Using default initial data.")
                return initial_data
        else:
            print("Error: Config file is empty. Using default initial data.")
            return initial_data
    else:
        with open('config.json', 'w') as f:
            json.dump(initial_data, f, indent=4)
        print("Config file created with initial data.")
        return initial_data


def save_settings(settings_data):
    with open('config.json', 'w') as f:
        json.dump(settings_data, f, indent=4)
