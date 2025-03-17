from flask import *
from database import *
from werkzeug.security import *
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user'] 
        db = get_database()
        user_result = db.execute("SELECT * FROM users WHERE email = ?",[user]).fetchone()
    return user_result

@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'quizapp_db'):
        g.quizapp_db.close()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home',methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login',methods=['GET', 'POST'])
def contact():
    return render_template('login.html')

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        db = get_database()
        email = request.form['email']
        username = request.form['name']
        password = request.form['password']
        hashed_password = generate_password_hash(password,method='sha256')

        cp = request.form['confirm_password']
        if password == cp:
            db.execute("INSERT INTO users (email,name,password) VALUES (?,?,?)",[email,username,hashed_password])
            db.commit()
            session['user'] = email
            return render_template('login.html')
        else:
            return 'Passwords do not match'
    return render_template('register.html')

@app.route('/logout')
def logout():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)