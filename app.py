import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # تم تحديث الجدول ليشمل اسم البنت والجروب
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            group_name TEXT NOT NULL,
            task_name TEXT NOT NULL,
            notes TEXT,
            file_name TEXT NOT NULL,
            submitted_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-task', methods=['GET'])
def submit_task_page():
    return render_template('submit_task.html')

@app.route('/submit-task', methods=['POST'])
def handle_task_submission():
    student_name = request.form.get('student_name')
    group_name = request.form.get('group_name')
    task_name = request.form.get('task_name')
    notes = request.form.get('notes')
    file = request.files.get('task_file')
    
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO submissions (student_name, group_name, task_name, notes, file_name, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_name, group_name, task_name, notes, file.filename, current_time))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    return "حدث خطأ أثناء رفع الملف."

@app.route('/admin/submissions')
def view_submissions():
    ADMIN_PASSWORD = "pinkmind2026"
    user_password = request.args.get('password')
    
    if user_password != ADMIN_PASSWORD:
        return "<h1 style='color:red; text-align:center; margin-top:50px; font-family:sans-serif;'>عذراً، هذه الصفحة محمية ولا تملك صلاحية الدخول! 🔒</h1>", 403

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # جلب كل البيانات الجديدة وترتيبها
    cursor.execute('SELECT student_name, group_name, task_name, notes, file_name, submitted_at FROM submissions ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return render_template('submissions_list.html', submissions=rows)

if __name__ == '__main__':
    app.run(debug=True)