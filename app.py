from flask import Flask, request, redirect, render_template, send_from_directory, session, flash, url_for
import os
# import secrets



app = Flask(__name__)

# app.secret_key = secrets.token_hex(32)
app.secret_key = '2fbb9a8d5f4c48760d97f4531cd5bdf4'



UPLOAD_FOLDER = 'uploads'
PASSWORD = 'prsn'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
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
            f = request.files['file']
            if f.filename:
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
                flash('uploaded successfuly')
        elif 'delete' in request.form:
            os.remove(os.path.join(UPLOAD_FOLDER, request.form['delete']))
            flash('deleted successfuly')
        elif 'rename_old' in request.form and 'rename_new' in request.form:
            os.rename(
                os.path.join(UPLOAD_FOLDER, request.form['rename_old']),
                os.path.join(UPLOAD_FOLDER, request.form['rename_new'])
            )
            flash('file renamed successfully')
        elif 'change_password' in request.form and 'new_password' in request.form:
            global PASSWORD
            PASSWORD = request.form['new_password']
            flash('Password changed successfully!')
        return redirect(url_for('index'))

    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if not session.get('logged_in'):
        flash("you dont have access")
        return redirect(url_for('login'))
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
