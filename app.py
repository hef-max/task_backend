from flask import Flask, render_template, redirect, Blueprint, request, flash, url_for, Response
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
# model = Model()
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

User = User()

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
        return User.query.get(int(id))
    return app

@app.route('/', methods=['GET', 'POST'])
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                with sqlite3.connect('database.db') as db:
                    cursor = db.cursor()
                    cursor.execute(f"SELECT first_name FROM `user` WHERE email='{email}';")
                    # first_name = name.append(cursor.fetchall())
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True) 
                return redirect(url_for('index'))
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

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

######################## dashboard ###########################################

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True
@app.route('/pie-plot')
def pie_png():
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	y = np.array([3, 8, 2, 8])
	mylabels = ["Handphone", "Laptop", "Notebook", "Macbox"]
	axis.pie(y, labels=mylabels)
	output = io.BytesIO()
	FigureCanvas(fig).print_png(output)
	return Response(output.getvalue(), mimetype='image/png')

@app.route('/print-plot')
def plot_png():
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	x = np.array(["Handphone", "Laptop", "Notebook", "Macbox"])
	y = np.array([3, 8, 1, 8])
	axis.bar(x,y)
	output = io.BytesIO()
	FigureCanvas(fig).print_png(output)
	return Response(output.getvalue(), mimetype='image/png')

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # first_name = name[0][0][0]
    items = {
        "name": 'Widi Susanto'
    }
    return render_template('index.html', items=items,  user=current_user)

@app.route('/profile')
def myprofile():
    # first_name = name[0][0][0]
    items = {
       "name": 'Widi Susanto'
    }
    return render_template('myprofile.html', items=items)

@app.route('/dashboard')
def dashboard():
    # first_name = name[0][0][0]
    items = {
        "name": 'Widi Susanto',
        "cuaca": cuaca.read()
    }
    return render_template('dashboard.html', items=items)

@app.route('/orders')
def orders():
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM barang;")
    # first_name = name[0][0][0]
    items = {
        "name": 'Widi Susanto',
        "data": cursor.fetchall()
    }
    return render_template("orders.html", items=items)

@app.route('/settings')
def settings():
    items = {
       "name": 'Widi Susanto'
    }
    return render_template('settings.html', items=items)

@auth.route('/logout')
@login_required
def logout():
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