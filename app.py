from flask import abort
import mimetypes
from flask import Flask, request, redirect, render_template, send_from_directory, session, flash, url_for
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

@app.route('/preview/<path:filename>')
def preview_file(filename):
    if not session.get('logged_in'):
        flash("you dont have access")
        return redirect(url_for('login'))
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return abort(404)
    mime, _ = mimetypes.guess_type(file_path)
    if mime and mime.startswith('image/'):

        return render_template('preview.html', filename=filename, filetype='image')
    elif mime and (mime.startswith('text/') or filename.lower().endswith(('.py','.txt','.md','.html','.css','.js','.json','.csv'))):

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        return render_template('preview.html', filename=filename, filetype='text', content=content)
    else:

        return render_template('preview.html', filename=filename, filetype='other')

# app.secret_key = secrets.token_hex(32)
app.secret_key = '2fbb9a8d5f4c48760d97f4531cd5bdf4'



UPLOAD_FOLDER = 'uploads'


PASSWORD_FILE = 'password.txt'


if not os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE, 'w') as f:
        f.write(generate_password_hash('nati'))


def get_password_hash():
    with open(PASSWORD_FILE, 'r') as f:
        return f.read().strip()


def set_password_hash(new_hash):
    with open(PASSWORD_FILE, 'w') as f:
        f.write(new_hash)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password_hash = get_password_hash()
        if check_password_hash(password_hash, request.form['password']):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('password is incorrrect')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('you Loged out')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':

        if 'file' in request.files:
            files = request.files.getlist('file')
            uploaded = 0
            for f in files:
                if f.filename:
                    
                    rel_path = f.filename
                    dest_path = os.path.join(app.config['UPLOAD_FOLDER'], rel_path)
                    dest_dir = os.path.dirname(dest_path)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir, exist_ok=True)
                    f.save(dest_path)
                    uploaded += 1
            if uploaded:
                flash(f'{uploaded} file(s) uploaded successfully')
        elif 'delete' in request.form:
            target = os.path.join(UPLOAD_FOLDER, request.form['delete'])
            if os.path.isdir(target):
                import shutil
                shutil.rmtree(target)
                flash('Folder deleted successfully')
            else:
                os.remove(target)
                flash('File deleted successfully')
        elif 'rename_old' in request.form and 'rename_new' in request.form:
            old_path = os.path.join(UPLOAD_FOLDER, request.form['rename_old'])
            new_path = os.path.join(UPLOAD_FOLDER, request.form['rename_new'])

            if os.path.isdir(old_path):
                new_dir_parent = os.path.dirname(new_path)
                if not os.path.exists(new_dir_parent):
                    os.makedirs(new_dir_parent, exist_ok=True)
            os.rename(old_path, new_path)
            flash('file/folder renamed successfully')
        elif 'change_password' in request.form and 'new_password' in request.form:
            new_hash = generate_password_hash(request.form['new_password'])
            set_password_hash(new_hash)
            flash('Password changed successfully!')
        return redirect(url_for('index'))

    def build_tree(base_dir):
        tree = {}
        for root, dirs, files in os.walk(base_dir):
            rel_root = os.path.relpath(root, base_dir)
            node = tree
            if rel_root != '.':
                for part in rel_root.split(os.sep):
                    node = node.setdefault(part, {})
            for d in dirs:
                node.setdefault(d, {})
            for f in files:
                node[f] = None  
        return tree

    files_tree = build_tree(UPLOAD_FOLDER)
    return render_template('index.html', files_tree=files_tree)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if not session.get('logged_in'):
        flash("you dont have access")
        return redirect(url_for('login'))
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
