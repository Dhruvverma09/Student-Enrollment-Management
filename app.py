from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
print("DB USER:", os.getenv("DB_USER"))
print("DB PASSWORD:", os.getenv("DB_PASSWORD"))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# MySQL database connection config
db_config = {
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST", "localhost"),
    'port': os.getenv("DB_PORT", "3306"),
    'database': os.getenv("DB_NAME", "student_enrollment")
}

# Retrieve admin credentials from environment variables
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Route to home page with options for student registration and admin login
@app.route('/')
def home():
    return render_template('home.html')

# Route to display the enrollment form
@app.route('/register')
def enrollment_form():
    return render_template('index.html')

# Route to handle student enrollment form submission
@app.route('/enroll', methods=['POST'])
def enroll_student():
    student_name = request.form['student_name']
    father_name = request.form['father_name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    city = request.form['city']
    state = request.form['state']
    pin_code = request.form['pin_code']
    department = request.form['department']
    course = request.form['course']
    comments = request.form['comments']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    sql = '''INSERT INTO students 
             (student_name, father_name, email, phone, address, city, state, pin_code, department, course, comments)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

    values = (student_name, father_name, email, phone, address, city, state, pin_code, department, course, comments)

    try:
        cursor.execute(sql, values)
        conn.commit()
        return redirect(url_for('success'))  # Redirect to success page
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        flash("There was an error enrolling the student.")
        return redirect(url_for('enrollment_form'))
    finally:
        cursor.close()
        conn.close()

@app.route('/success')
def success():
    return render_template('success.html')

# Route to display the admin login page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Attempting login with username: {username}")  # Debugging line

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

# Admin dashboard route to view all student records
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html', students=students)

# Route to edit a student record
@app.route('/admin/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        student_name = request.form['student_name']
        father_name = request.form['father_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        pin_code = request.form['pin_code']
        department = request.form['department']
        course = request.form['course']
        comments = request.form['comments']

        sql = '''UPDATE students SET 
                 student_name = %s, father_name = %s, email = %s, phone = %s, 
                 address = %s, city = %s, state = %s, pin_code = %s, 
                 department = %s, course = %s, comments = %s
                 WHERE id = %s'''
        values = (student_name, father_name, email, phone, address, city, state, pin_code, department, course, comments, student_id)

        try:
            cursor.execute(sql, values)
            conn.commit()
            session['success'] = True  # Set success flag
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
            flash("There was an error updating the student record.")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('edit_student', student_id=student_id))  # Redirect back to the edit page with success message
    else:
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_student.html', student=student)

# Route to delete a student record
@app.route('/admin/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Student record deleted successfully!")
    return redirect(url_for('admin_dashboard'))

# Logout route for admin
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
