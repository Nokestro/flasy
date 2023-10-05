from flask import Flask, render_template, request, flash, session, redirect, url_for, g, abort, make_response
import sqlite3
import os

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from Fdatabase import FDataBase
from forms import LoginForm

# Конфигурация
DATABASE =  '/tmp/flsite.db'
SECRET_KEY = 'fasko234k2podsa3r233ew'
DEBUG = True
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь пожалуйста для доступа к контенту"
login_manager.login_message_category = "sussecc"

@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, dbase)


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

dbase = None
@app.before_request
def before_request():
    """Установка соединения с БД перед запросом"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


menu = [{"name":'catalog', "url":'catalog'},
        {"name":'about', "url":'about'},
        {"name":'help', "url":'help'},
        {"name":'contact', "url":'contact'},
        {"name":'register', "url":'register'}]

@app.route("/index")
@app.route("/")
def index():
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

@app.route('/log', methods=["POST", "GET"])
def log():
    if current_user.is_authenticated:
        return redirect(url_for('uprofile'))

    form = LoginForm()
    if form.validate_on_submit():
    user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('uprofile'))

        flash('Невераня пара пароль/логин', 'error')

    return render_template('kitty/log.html', menu=dbase.getMenu(), title='Авторизация', form=form)

    # if request.method == "POST":
    #     user = dbase.getUserByEmail(request.form['email'])
    #     if user and check_password_hash(user['psw'], request.form['psw']):
    #         userlogin = UserLogin().create(user)
    #         rm = True if request.form.get('remainme') else False
    #         login_user(userlogin, remember=rm)
    #         return redirect(request.args.get('next') or url_for('uprofile'))
    #     flash('Невераня пара пароль/логин', 'error')

    # return render_template('kitty/log.html', title='Логин', menu=dbase.getMenu())
@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
            and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('log'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")
    return render_template('kitty/register.html', title='Логин', menu=dbase.getMenu())


@app.route('/add_posts', methods = ['POST', 'GET'])
def addPosts():

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
@login_required
def showPost(alias):
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


@app.route('/uprofile')
@login_required
def uprofile():
    return render_template('kitty/uprofile.html', menu = dbase.getMenu(), title="profile")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))



@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img: return ""
    h=make_response(img)
    h.headers['Content-Type'] = 'image/png'


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                    return redirect(url_for('profile'))
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))
# Обработчик ошибок

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu)


if __name__ == "__main__":
    app.run(debug=True)
