from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random

app = Flask(__name__)

# Database Connection Helper
def get_db_connection():
    conn = sqlite3.connect('hospital.db')
    conn.row_factory = sqlite3.Row  # Allows column access by name
    return conn

# Initialize Database Table
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            disease TEXT NOT NULL,
            doctor TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home Page Route
@app.route('/')
def index():
    return render_template('index.html')

# Register Patient Route
@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        disease = request.form['disease']
        doctor = request.form['doctor']
        token = random.randint(100, 999)

        conn = get_db_connection()
        conn.execute('INSERT INTO patients (token, name, age, gender, disease, doctor) VALUES (?, ?, ?, ?, ?, ?)',
                     (token, name, age, gender, disease, doctor))
        conn.commit()
        conn.close()
        return redirect(url_for('patient_list'))
    return render_template('register.html')

# View & Search Patient List Route
@app.route('/patients')
def patient_list():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    
    if search_query:
        patients = conn.execute(
            "SELECT * FROM patients WHERE name LIKE ? OR disease LIKE ?", 
            ('%' + search_query + '%', '%' + search_query + '%')
        ).fetchall()
    else:
        patients = conn.execute('SELECT * FROM patients').fetchall()
        
    conn.close()
    return render_template('patients.html', patients=patients, search_query=search_query)

# Edit Patient Route
@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        disease = request.form['disease']

        conn.execute('UPDATE patients SET name = ?, age = ?, gender = ?, disease = ? WHERE id = ?',
                     (name, age, gender, disease, id))
        conn.commit()
        conn.close()
        return redirect(url_for('patient_list'))

    conn.close()
    return render_template('edit.html', patient=patient)

# Delete Patient Route
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM patients WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('patient_list'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
  
