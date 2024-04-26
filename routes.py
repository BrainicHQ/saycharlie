from flask import request, redirect, render_template, url_for
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


def settings():
    settings_data = load_settings()
    return render_template('settings.html', columns=settings_data['columns'], buttons=settings_data['buttons'])
