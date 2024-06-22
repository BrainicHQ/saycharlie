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
import subprocess
import uuid

from flask import request, redirect, render_template, url_for, jsonify
from werkzeug.utils import secure_filename

from config import load_settings, save_settings
import urllib.parse
import os
import logging
from threading import Thread

from svx_api import get_active_profile

UPLOAD_FOLDER = 'profile-uploads/'
ALLOWED_EXTENSIONS = {'conf'}

# Set up logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(module)s - %(levelname)s: %(message)s',
    filename='/tmp/saycharlie.log',
    filemode='a'  # Use 'a' to append to the file
)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def file_manager():
    settings_data = load_settings()

    # Ensure UPLOAD_FOLDER exists; create it if it doesn't
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if request.method == 'POST':
        # Check if the post request has the file part
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            return redirect(url_for('file_manager'))

    files = os.listdir(UPLOAD_FOLDER)
    file_contents = {file: open(os.path.join(UPLOAD_FOLDER, file), 'r').read() for file in files if
                     os.path.isfile(os.path.join(UPLOAD_FOLDER, file))}
    return render_template('file_manager.html', files=files, file_contents=file_contents,
                           app_background=settings_data['app_background'])


def edit_file(filename):
    content = request.form['content']
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, 'w') as file:
        file.write(content)
    return redirect(url_for('file_manager'))


def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    os.remove(file_path)
    return redirect(url_for('file_manager'))


def dashboard():
    settings_data = load_settings()
    active_profile, _ = get_active_profile()
    # get file name from the path
    profile_name = urllib.parse.unquote(os.path.basename(active_profile))

    return render_template('dashboard.html', buttons=settings_data['buttons'],
                           columns=settings_data['columns'], app_background=settings_data['app_background'],
                           svx_active_profile=profile_name)


def category(category_uuid):
    settings_data = load_settings()
    category_data = settings_data['buttons']
    active_profile, _ = get_active_profile()
    # get file name from the path
    profile_name = urllib.parse.unquote(os.path.basename(active_profile))
    buttons_in_category = []
    # if button label is equal to category name, return buttons in that category
    for button in category_data:
        if button.get('category') == category_uuid:
            buttons_in_category.append(button)
    return render_template('category.html', app_background=settings_data['app_background'],
                           columns=settings_data['columns'],
                           buttons_in_category=buttons_in_category,
                           svx_active_profile=profile_name
                           )


def get_buttons():
    try:
        settings_data = load_settings()  # Assuming this function loads your settings
        # Get all buttons that are categories
        buttons = [button for button in settings_data['buttons']]
        return jsonify(buttons), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


def add_button():
    try:
        settings_data = load_settings()
        data = request.json  # Access JSON data sent by Alpine.js
        new_uuid = str(uuid.uuid4())  # Generate a new UUID for each new button

        new_button = {
            'id': new_uuid,
            'label': data['label'],
            'color': data['color'],
            'fontColor': data['font_color'],
            'category': data.get('category'),
            'isCategory': data.get('isCategory', False)
        }

        if new_button['isCategory']:
            new_button['action'] = ''
            new_category = {
                'label': new_button['label'],
                'buttons': []
            }
            settings_data.setdefault('categories', []).append(new_category)
        else:
            new_button['action'] = data['action']

        settings_data['buttons'].append(new_button)
        save_settings(settings_data)
        return jsonify({
            'success': True,
            'message': 'Button added successfully',
            'id': new_uuid
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


def update_button(uuid_id):
    try:
        settings_data = load_settings()
        data = request.json
        buttons = settings_data['buttons']
        uuid_id_str = str(uuid_id)  # Ensure uuid_id is treated as a string

        # Find the index of the button to update
        index = next((i for i, button in enumerate(buttons) if button['id'] == uuid_id_str), None)
        if index is None:
            return jsonify({"status": "error", "message": "Button not found"}), 404

        new_label = data.get('label', buttons[index]['label'])  # Default to current label if not provided
        new_color = data.get('color', buttons[index]['color'])  # Default to current color if not provided
        new_font_color = data.get('font_color',
                                  buttons[index]['fontColor'])  # Default to current font color if not provided
        new_category = data.get('category', buttons[index]['category'])  # Default to current category if not provided
        new_is_category = data.get('isCategory',
                                   buttons[index]['isCategory'])  # Default to current isCategory if not provided
        new_action = data.get('action', buttons[index]['action'])  # Default to current action if not provided

        # Update the button's label, color, font color, category, isCategory, and action
        buttons[index]['label'] = new_label
        buttons[index]['color'] = new_color
        buttons[index]['fontColor'] = new_font_color
        buttons[index]['category'] = new_category
        buttons[index]['isCategory'] = new_is_category
        buttons[index]['action'] = new_action

        # If the button is a category, update the category label
        if new_is_category:
            category_index = next((i for i, category in enumerate(settings_data.get('categories', [])) if
                                   category['label'] == buttons[index]['label']), None)
            if category_index is not None:
                settings_data['categories'][category_index]['label'] = new_label

        save_settings(settings_data)
        return jsonify({"status": "success", "message": "Button updated successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


def delete_button(uuid_id):
    try:
        settings_data = load_settings()
        buttons = settings_data['buttons']
        uuid_id_str = str(uuid_id)

        # Find the index and check if it's a category
        button_to_delete = next((button for button in buttons if button['id'] == uuid_id_str), None)
        if button_to_delete is None:
            return jsonify({"status": "error", "message": "Button not found"}), 404

        if button_to_delete.get('isCategory', False):
            # It's a category, delete all associated buttons
            buttons = [button for button in buttons if
                       button['category'] != uuid_id_str and button['id'] != uuid_id_str]
        else:
            # It's not a category, just delete this button
            buttons = [button for button in buttons if button['id'] != uuid_id_str]

        settings_data['buttons'] = buttons
        save_settings(settings_data)
        return jsonify({"status": "success", "message": "Button deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


def set_columns():
    try:
        settings_data = load_settings()
        data = request.json
        columns = int(data['columns'])
        settings_data['columns'] = columns
        save_settings(settings_data)
        return jsonify({'success': True, 'message': 'Columns updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


def app_background():
    try:
        settings_data = load_settings()
        data = request.json
        app_background = data['background']
        settings_data['app_background'] = app_background
        save_settings(settings_data)
        return jsonify({'success': True, 'message': 'Background color updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


def get_talk_groups_data():
    settings_data = load_settings()
    return jsonify(settings_data.get('talk_groups', [])), 200


def get_group_name(number):
    settings_data = load_settings()
    groups = settings_data.get('talk_groups', [])
    group = next((group for group in groups if str(group['number']) == str(number)), None)
    if group is not None:
        return group['name']
    return None


def add_talk_group():
    settings_data = load_settings()
    data = request.get_json()
    new_uuid = str(uuid.uuid4())  # Generate a new UUID for each new group
    talk_group = {
        'id': new_uuid,
        'name': data['name'],
        'number': data['number']
    }

    if any(group['number'] == talk_group['number'] for group in settings_data.get('talk_groups', [])):
        return jsonify({"status": "error", "message": "Talk group number already exists"}), 400

    settings_data.setdefault('talk_groups', []).append(talk_group)
    save_settings(settings_data)
    return jsonify(
        {"id": new_uuid, "status": "success", "message": f"Talk group {talk_group['name']} added successfully"}), 201


def update_talk_group(uuid_id):
    settings_data = load_settings()
    data = request.get_json()
    groups = settings_data.get('talk_groups', [])
    uuid_id_str = str(uuid_id)  # Ensure uuid_id is treated as a string

    # Find the index of the group to update
    index = next((i for i, group in enumerate(groups) if group['id'] == uuid_id_str), None)
    if index is None:
        return jsonify({"status": "error", "message": "Talk group not found"}), 404

    new_number = data.get('number')
    new_name = data.get('name', groups[index]['name'])  # Default to current name if not provided

    # Check if the new number is unique among other groups, except the current one being updated
    if new_number and any(group['number'] == new_number and group['id'] != uuid_id_str for group in groups):
        return jsonify({"status": "error", "message": "Talk group number already exists"}), 400

    # Update the group's number and name
    groups[index]['number'] = new_number if new_number is not None else groups[index]['number']
    groups[index]['name'] = new_name
    save_settings(settings_data)
    return jsonify({"status": "success", "message": "Talk group updated successfully"}), 200


def delete_talk_group(uuid_id):
    settings_data = load_settings()
    groups = settings_data.get('talk_groups', [])
    # Convert uuid_id to str in case it's not already a string
    uuid_id_str = str(uuid_id)

    index = next((i for i, group in enumerate(groups) if group['id'] == uuid_id_str), None)
    if index is None:
        return jsonify({"status": "error", "message": "Talk group not found"}), 404

    # Remove the group from the list
    del groups[index]
    settings_data['talk_groups'] = groups
    save_settings(settings_data)
    return jsonify({"status": "success", "message": "Talk group deleted successfully"}), 200


def settings():
    settings_data = load_settings()
    return render_template('settings.html', columns=settings_data['columns'], buttons=settings_data['buttons'],
                           talk_groups=settings_data.get('talk_groups', []),
                           app_background=settings_data['app_background'])


def system_reboot():
    try:
        result = subprocess.run(['sudo', 'reboot'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"success": True, "message": "System rebooting..."}), 200
        else:
            return jsonify({"success": False, "message": result.stderr}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


def system_shutdown():
    try:
        result = subprocess.run(['sudo', 'shutdown', 'now'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"success": True, "message": "System shutting down..."}), 200
        else:
            return jsonify({"success": False, "message": result.stderr}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


def async_restart_service():
    restart_result = subprocess.run(['sudo', 'systemctl', 'restart', 'saycharlie.service'], capture_output=True,
                                    text=True)
    if restart_result.returncode != 0:
        logging.error(f"Restart service error: {restart_result.stderr}")


def update_app():
    try:
        # Stash local changes
        stash_result = subprocess.run(['git', 'stash'], capture_output=True, text=True)
        if stash_result.returncode != 0:
            logging.error(f"Stash error: {stash_result.stderr}")
            return jsonify({"success": False, "message": "Failed to stash local changes."}), 500

        # Pull latest changes from remote
        pull_result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        if pull_result.returncode != 0:
            logging.error(f"Pull error: {pull_result.stderr}")
            return jsonify({"success": False, "message": "Failed to pull updates."}), 500

        # Check if requirements.txt was updated using git diff
        diff_result = subprocess.run(['git', 'diff', '--name-only', 'HEAD@{1}', 'HEAD'], capture_output=True, text=True)
        if 'requirements.txt' in diff_result.stdout:
            install_result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], capture_output=True,
                                            text=True)
            if install_result.returncode != 0:
                logging.error(f"Dependency installation error: {install_result.stderr}")
                return jsonify({"success": False, "message": "Failed to update dependencies."}), 500

        # Restart the service asynchronously
        restart_thread = Thread(target=async_restart_service)
        restart_thread.start()

        return jsonify({"success": True, "message": "App updated and restart initiated."}), 200

    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500
