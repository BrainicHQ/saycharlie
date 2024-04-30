import uuid

from flask import request, redirect, render_template, url_for, jsonify
from werkzeug.utils import secure_filename

from config import load_settings, save_settings
import urllib.parse
import os

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'conf'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def file_manager():
    if request.method == 'POST':
        # Check if the post request has the file part
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            return redirect(url_for('file_manager'))

    files = os.listdir(UPLOAD_FOLDER)
    file_contents = {file: open(os.path.join(UPLOAD_FOLDER, file), 'r').read() for file in files}
    return render_template('file_manager.html', files=files, file_contents=file_contents)


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

    for button in settings_data['buttons']:
        if button.get('isCategory'):
            button['encoded_label'] = urllib.parse.quote(button['label'])

    return render_template('dashboard.html', buttons=settings_data['buttons'],
                           columns=settings_data['columns'], app_background=settings_data['app_background'])


def category(category_name):
    settings_data = load_settings()
    category_data = settings_data['buttons']
    buttons_in_category = []
    # if button label is equal to category name, return buttons in that category
    for button in category_data:
        if 'category' in button and button['category'] == category_name:
            buttons_in_category.append(button)
    return render_template('category.html', app_background=settings_data['app_background'],
                           columns=settings_data['columns'],
                           buttons_in_category=buttons_in_category)


def add_button():
    if request.method == 'POST':
        settings_data = load_settings()
        # Process form submission and update button settings
        new_button = {
            'label': request.form['label'],
            'color': request.form['color'],
            'category': request.form.get('category'),
            'isCategory': 'parent_category' in request.form
        }

        if new_button['isCategory']:
            new_button['action'] = ''
            new_category = {
                'label': new_button['label'],
                'buttons': []
            }
            settings_data.setdefault('categories', []).append(new_category)
        else:
            new_button['action'] = request.form['action']

        settings_data['buttons'].append(new_button)
        save_settings(settings_data)
        return redirect('/')


def set_columns():
    if request.method == 'POST':
        settings_data = load_settings()
        columns = int(request.form['columns'])
        settings_data['columns'] = columns
        save_settings(settings_data)
        return redirect('/')


def app_background():
    if request.method == 'POST':
        settings_data = load_settings()
        app_background = request.form['app_background']
        settings_data['app_background'] = app_background
        save_settings(settings_data)
        return redirect('/')


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
                           talk_groups=settings_data.get('talk_groups', []))
