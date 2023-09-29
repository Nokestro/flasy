from flask import Flask, render_template, request, flash, session, redirect, url_for, g, abort, make_response
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
    return render_template("kitty/index.html", menu=dbase.getMenu(), title = 'home', posts=dbase.getPostsAnonce())

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

@app.route('/add_posts', methods = ['POST', 'GET'])
def addPosts():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['title']) > 2 and len(request.form['text']) > 10:
            res = dbase.addPosts(request.form['title'], request.form['text'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')
    return render_template('kitty/add_posts.html', menu=dbase.getMenu(), title='Добавление статьи')

@app.route('/post/<alias>')
def showPost(alias):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('kitty/post.html', menu=dbase.getMenu(), title=title, post=post)

@app.route('/acclogin')
def acclogin():
    log = ''
    if request.cookies.get('logged'):
        log = request.cookies.get('logged')

    res = make_response(f"<h1>Форма авторизации</h1><p>logged: {log}</p>")
    res.set_cookie("logged", "yes", 30*24*3600)
    return res

@app.route('/acclogout')
def acclogout():
    res = make_response(f"<p>Вы больше не авторезированы</p>")
    res.set_cookie("logged", "", 0)
    return res


@app.route('/visit')
def visit():
    if 'visits' in session:
        session['visits'] = session.get('visits')+1
    else:
        session['visits'] = 1
    return f"<p>Число просмотров = {session['visits']}</p>"


# Обработчик ошибок

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu)


if __name__ == "__main__":
    app.run(debug=True)
