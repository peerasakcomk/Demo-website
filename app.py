from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = 'chicken_shop.db'

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# สร้างฐานข้อมูลและข้อมูลเริ่มต้น (รันครั้งแรก)
def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS units (id INTEGER PRIMARY KEY, name TEXT)''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            image TEXT,
            unit_id INTEGER
        )
    ''')
    
    # เพิ่มข้อมูลหมวดหมู่และหน่วยนับเริ่มต้น ถ้ายังไม่มี
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        conn.executemany("INSERT INTO categories (name) VALUES (?)", [('ไก่ทอด',), ('เซ็ตสุดคุ้ม',), ('ของทานเล่น',), ('เครื่องดื่ม',)])
        conn.executemany("INSERT INTO units (name) VALUES (?)", [('ชิ้น',), ('เซ็ต',), ('แก้ว',), ('กล่อง',)])
        conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db()
    foods = conn.execute('''
        SELECT f.*, c.name as cat_name, u.name as unit_name 
        FROM foods f 
        LEFT JOIN categories c ON f.category_id = c.id 
        LEFT JOIN units u ON f.unit_id = u.id
    ''').fetchall()
    conn.close()
    return render_template('index.html', foods=foods)

@app.route('/add', methods=('GET', 'POST'))
def add():
    conn = get_db()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        image = request.form['image']
        category_id = request.form['category_id']
        unit_id = request.form['unit_id']

        conn.execute('INSERT INTO foods (name, price, stock, image, category_id, unit_id) VALUES (?, ?, ?, ?, ?, ?)',
                     (name, price, stock, image, category_id, unit_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    categories = conn.execute('SELECT * FROM categories').fetchall()
    units = conn.execute('SELECT * FROM units').fetchall()
    conn.close()
    return render_template('add.html', categories=categories, units=units)

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db()
    food = conn.execute('SELECT * FROM foods WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        image = request.form['image']
        category_id = request.form['category_id']
        unit_id = request.form['unit_id']

        conn.execute('''
            UPDATE foods SET name = ?, price = ?, stock = ?, image = ?, category_id = ?, unit_id = ?
            WHERE id = ?
        ''', (name, price, stock, image, category_id, unit_id, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    categories = conn.execute('SELECT * FROM categories').fetchall()
    units = conn.execute('SELECT * FROM units').fetchall()
    conn.close()
    return render_template('edit.html', food=food, categories=categories, units=units)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute('DELETE FROM foods WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)