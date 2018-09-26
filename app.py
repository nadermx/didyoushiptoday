from flask import Flask, render_template, request
from flask_login import LoginManager, current_user, login_user
from pony.orm import *
import models
from datetime import datetime
import redis
# from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object('config')

# CSRFProtect(app)


r = redis.StrictRedis(host='localhost', port=6379, db=0)

login_manager = LoginManager()
login = LoginManager(app)

@login.user_loader
def load_user(id):
    return models.User.get(id=id)

@login.unauthorized_handler
def unauthorized():
    return 401

@app.route('/yes', methods=['POST'])
def yes():
    if current_user.is_authenticated:
        models.Ship(yes=True, user=models.User[current_user.id], dt_shipped=datetime.utcnow)
    else:
        anon_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        if not r.get(anon_ip):
            end_of_day = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999)
            r.set(anon_ip, anon_ip)
            r.expireat(anon_ip, end_of_day)
            models.Ship(yes=True, dt_shipped=datetime.utcnow())
    today_utc = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    shipped = models.select(s for s in models.Ship if s.dt_shipped > today_utc)
    yes = shipped.filter(lambda y: y.yes).count()
    return render_template('yes.html', shipped=shipped.count(), yes=yes, percent=int(yes)/int(shipped.count()))

@app.route('/no', methods=['POST'])
def no():
    if current_user.is_authenticated:
        models.Ship(no=True, user=models.User[current_user.id], dt_shipped=datetime.utcnow)
    else:
        anon_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        if not r.get(anon_ip):
            end_of_day = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999)
            r.setex(anon_ip, 'visited_today', end_of_day)
            models.Ship(no=True, dt_shipped=datetime.utcnow())
    today_utc = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    shipped = models.select(s for s in models.Ship if s.dt_shipped > today_utc)
    no = shipped.filter(lambda n: n.no).count()
    return render_template('no.html', shipped=shipped.count(), no=no, percent=int(no)/int(shipped.count()))



@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        data = request.form
        email = data['email'].lower()
        password = data['password']
        user = models.User.get(email=email)
        if not user:
            return render_template('login.html', error='User does not exist')
        if not user.verify_password(password):
            return render_template('login.html', error='Incorrect Password')
        login_user(user)
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        data = request.form
        username = data['username'].lower()
        email = data['email'].lower()
        password = data['password']
        if not email or not password:
            return render_template('signup.html', error="missing email or password")
        user = models.User.get(email=email)
        if user:
            return render_template('signup.html', error="Email already exists")
        user = models.User(email=email)
        user.hash_password(password)
        models.commit()
        login_user(user)
        return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')

