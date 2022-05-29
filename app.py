from flask import Flask, render_template, redirect, Blueprint, request, flash, url_for, Response, session
from api import *
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from os import path
import sqlite3
from flask_login import LoginManager, UserMixin


app = Flask(__name__, template_folder='templates')
cuaca = Api()
db = SQLAlchemy()
DB_NAME = "database.db"
views = Blueprint('views', __name__)
auth = Blueprint('auth', __name__)
name = []

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

user_class = User()

def create_database(app):
    if not path.exists('/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

def create_app():
    app.config['SECRET_KEY'] = 'xxxx'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return user_class.query.get(int(id))
    return app

@app.route('/', methods=['GET', 'POST'])
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = user_class.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                with sqlite3.connect('database.db') as db:
                    cursor = db.cursor()
                    cursor.execute(f"SELECT first_name FROM `user` WHERE email='{email}';")
                    first_name = cursor.fetchall()
                    name.append(first_name[0][0])
                session['logged_in'] = True
                session['username'] = first_name[0][0]
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True) 
                return redirect(url_for('myprofile'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = user_class.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 7 characters.', category='error')
        else:
            print("masuk else")
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            session['logged_in'] = True
            session['username'] = first_name
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('myprofile'))

    return render_template("sign_up.html", user=current_user)


######################## dashboard ###########################################

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True
@app.route('/print-plot')
def plot_png():
    a = []
    b = []
    c = []
    d = []
    
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute('SELECT nama_barang FROM `barang`;')
        for nama_barang in cursor.fetchall():
            if nama_barang[0] == 'Handphone':
                with sqlite3.connect('database.db') as db:
                    cursor = db.cursor()
                    cursor.execute('SELECT SUM(jumlah_barang) AS TotalItemsOrdered FROM barang WHERE nama_barang="Handphone";')
                    jumlah_barang = cursor.fetchall()

                    a.append(jumlah_barang[0])

            if nama_barang[0] == 'Laptop':
                with sqlite3.connect('database.db') as db:
                    cursor = db.cursor()
                    cursor.execute('SELECT SUM(jumlah_barang) AS TotalItemsOrdered FROM barang WHERE nama_barang="Laptop";')
                    jumlah_barang = cursor.fetchall()

                    b.append(jumlah_barang[0])

            if nama_barang[0] == 'Noteboox':
                with sqlite3.connect('database.db') as db:
                    cursor = db.cursor()
                    cursor.execute('SELECT SUM(jumlah_barang) AS TotalItemsOrdered FROM barang WHERE nama_barang="Noteboox";')
                    jumlah_barang = cursor.fetchall()

                    c.append(jumlah_barang[0])

            if nama_barang[0] == 'Macbox':
                with sqlite3.connect('database.db') as db:
                    cursor = db.cursor()
                    cursor.execute('SELECT SUM(jumlah_barang) AS TotalItemsOrdered FROM barang WHERE nama_barang="Macbox";')
                    jumlah_barang = cursor.fetchall()

                    d.append(jumlah_barang[0])
    if a == []:
        n = [(0)]
        a.append(n)
    if b == []:
        n = [(0)]
        b.append(n)
    if c == []:
        n = [(0)]
        c.append(n)
    if d == []:
        n = [(0)]
        d.append(n)

    print(a, b, c, d)

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    x = np.array(["Handphone", "Laptop", "Notebook", "Macbox"])
    y = np.array([a[0][0], b[0][0], c[0], d[0][0]])
    axis.bar(x,y)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html',  user=current_user)

@app.route('/profile')
def myprofile():
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f'SELECT * FROM user WHERE first_name="{name[0]}";')
        data = cursor.fetchall()
    items = {
        "email": data[0][1]
    }
    return render_template('myprofile.html', items=items)

@app.route('/dashboard')
def dashboard():
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM barang;")
    items = {
        "data": cursor.fetchall(), 
        "cuaca": cuaca.read()
    }
    return render_template('dashboard.html', items=items)

@app.route('/orders')
def orders():
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM barang;")
    items = {
        "data": cursor.fetchall()
    }
    return render_template("orders.html", items=items)

@auth.route('/logout')
@login_required
def logout():
    name.clear()
    logout_user()
    return redirect('login')


######################################## CRUD ###################################################

@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == 'POST':
        ID = request.form['id']
        kode_barang = request.form['kode_barang']
        nama_barang = request.form['nama_barang']
        jumlah_barang = request.form['jumlah_barang']
        harga_barang = request.form['harga_barang']

        with sqlite3.connect('database.db') as db:
            cursor = db.cursor()
            cursor.execute(f"INSERT INTO barang VALUES ({ID}, '{kode_barang}', '{nama_barang}', {jumlah_barang}, {harga_barang});")
        db.commit()
        flash("Employee Inserted Successfully")

        return redirect(url_for('orders'))

@app.route('/update', methods = ['GET', 'POST'])
def update():
    if request.method == 'POST':
        ID = request.form.get('id')
        kode_barang = request.form['kode_barang']
        nama_barang = request.form['nama_barang']
        jumlah_barang = request.form['jumlah_barang']
        harga_barang = request.form['harga_barang']

        with sqlite3.connect('database.db') as db:
            cursor = db.cursor()
            cursor.execute(f"UPDATE barang SET kode_barang='{kode_barang}', nama_barang='{nama_barang}', jumlah_barang={jumlah_barang}, harga_barang={harga_barang};")
        db.commit()
        flash("Employee Updated Successfully")

        return redirect(url_for('orders'))

@app.route('/hapus/<string:id_data>', methods=["GET"])
def hapus(id_data):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(f"DELETE FROM `barang` WHERE id={id_data};")
        db.commit()
    return redirect("/orders")

if __name__ == '__main__':
	create_app()
	app.run(debug=True)