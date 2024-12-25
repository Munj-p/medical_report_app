import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from login import login as login_user, is_logged_in, logout as logout_user
import secrets
import uuid

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Directory for uploaded images
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Sample reports data
reports = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not email or not password:
            return render_template('login.html', error="All fields are required.")
        if login_user(email, password):
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('dashboard.html', reports=reports)

@app.route('/add_report', methods=['GET', 'POST'])
def add_report():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        image = request.files['image']

        if not title or not description or 'image' not in request.files:
            return render_template('add_report.html', error="All fields are required.")
        
        if image and allowed_file(image.filename):
            image_filename = f"{uuid.uuid4().hex}_{image.filename}"
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            image.save(image_path)

            reports.append({
                'id': len(reports) + 1,
                'title': title,
                'description': description,
                'image_url': url_for('uploaded_file', filename=image_filename)
            })
            return redirect(url_for('dashboard'))
        else:
            return render_template('add_report.html', error="Invalid file type.")
    
    return render_template('add_report.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/delete_report/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    global reports
    reports = [report for report in reports if report['id'] != report_id]
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
