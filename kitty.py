from flask import Flask, render_template, request, flash, session, redirect, url_for, g
import sqlite3
import os

from Fdatabase import FDataBase

# Конфигурация
DATABASE =  '/tmp/flsite.db'
SECRET_KEY = 'fasko234k2podsa3r233ew'
DEBUG = True




app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

# База данных

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Функция для создания таблиц"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode = 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db






menu = [{"name":'catalog', "url":'catalog'},
        {"name":'about', "url":'about'},
        {"name":'help', "url":'help'},
        {"name":'contact', "url":'contact'},
        {"name":'register', "url":'register'}]

@app.route("/index")
@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template("kitty/index.html", menu=dbase.getMenu(), title = 'home')

@app.route("/contact", methods=["POST", "GET"])
def contact():


    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправления', category='error')

    return render_template("kitty/contact.html", menu=menu, title = 'contact')

@app.route('/profile/<username>')
def profile(username):
    return f'Профиль пользователя: {username}'

@app.route('/login', methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == "POST" and request.form['username'] == 'nokestro' and request.form['psw'] == '123':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))

    return  render_template('kitty/login.html', title = "Auth", menu=menu)
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu)


@app.route('/add_posts', methods = ['POST', 'GET'])
def add_posts():



if __name__ == "__main__":
    app.run(debug=True)
