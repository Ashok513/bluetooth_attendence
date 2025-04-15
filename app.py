from flask import Flask, render_template, request, redirect, url_for, session
import asyncio
from teacher.bluetooth_scan import scan_devices
from student_backend import student_auth  # Import student_auth


app = Flask(__name__)
app.secret_key = "teacher_secret_key_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Register the student Blueprint
app.register_blueprint(student_auth.student_bp)

# ------------------- Home & Role Selection -------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        role = request.form['role']
        if role == 'student':
            return redirect(url_for('student.student_login'))  # Correct route
        elif role == 'teacher':
            return redirect(url_for('teacher_login'))
    return render_template('index.html')

# Other teacher routes remain as-is...



# ------------------- Teacher Routes -------------------
@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        session["user"] = "teacher_email"
        return redirect(url_for('teacher_home'))
    return render_template('teacher/teacher_login.html')

@app.route('/teacher/home')
def teacher_home():
    return render_template('teacher/teacher_home.html')

@app.route('/teacher/register', methods=['GET', 'POST'])
def teacher_register():
    if request.method == 'POST':
        return redirect(url_for('teacher_login'))
    return render_template('teacher/teacher_register.html')

@app.route("/take-attendance")
def take_attendance():
    if "user" not in session:
        return redirect(url_for("teacher_login"))

    found_students = asyncio.run(scan_devices())
    
    
    import csv
    from datetime import datetime
    with open("attendance_log.csv", "a", newline="") as file:
        writer = csv.writer(file)
        for student in found_students:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([student['student_name'], student['roll_number'], now])
            student["time"] = now

    return render_template("teacher/attendance_list.html", students=found_students)
    
@app.route('/attendance-report')
def attendance_report():
    students = [
        {"student_name": "Ashok kumar", "roll_number": "22456", "time": "10:34:12"},
        {"student_name": "RAvi das", "roll_number": "8877", "time": "10:40:30"},
        {"student_name": "Aman Gupta", "roll_number": "3245", "time": "10:42:44"},
        
    ]
    return render_template('teacher/attendance_list.html', students=students)


   

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('teacher_login'))

if __name__ == '__main__':
    app.run(debug=True)
