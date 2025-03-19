from flask import *
from models import *
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

@app.route('/add_subject', methods=['POST', 'GET'])
def add_subject():
    user = get_current_user()
    
    if not user:
        return redirect(url_for('login'))  # Redirect if user is not authenticated

    if request.method == 'POST':
        db = get_database()
        subject = request.form.get('subject')  # Use .get() to avoid KeyError
        if subject:  # Ensure subject is not empty
            db.execute("INSERT INTO subjects (name) VALUES (?)", [subject])
            db.commit()
            return redirect(url_for('admin'))
        return "Error: Subject name cannot be empty", 400  # Handle empty input

    return render_template('add_subject.html', user=user)  # Always return something

@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'quizapp_db'):
        g.quizapp_db.close()

@app.route('/')
def index():
    user = get_current_user()
    return render_template('home.html',user = user)

@app.route('/home',methods=['GET'])
def home():
    user = get_current_user()
    return render_template('home.html',user = user)


@app.route('/about')
def about():
    user = get_current_user()
    return render_template('about.html',user = user)

@app.route('/admin')
def admin():
    user = get_current_user()
    if user:
        return render_template('admin_dashboard.html',user = user)
    
@app.route('/user')
def user():
    user = get_current_user()
    if user:
        return render_template('user_dashboard.html',user = user)
@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_database()
        try:
            email = request.form['email']
            password = request.form['password']
            role = request.form.get('role') 
            user = db.execute("select * from users where email = ?", [email]).fetchone()
            if user:
                if role == user['role']:
                    if check_password_hash(user['password'], password):
                        session['user'] = email
                        session['user_type'] = role
                        return redirect(url_for(role))
                    else:
                        return render_template('login.html', error1='Invalid Password')
                else:
                    return render_template('login.html', error1='Incorrect Role')
            else:
                return render_template('login.html',error1='Invalid User')
        except KeyError:
            return render_template('login.html', error2='Please fill in all fields')
            
    return render_template('login.html')

@app.route('/add_chapter',methods=['POST','GET'])
def add_chapter():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_database()
        chapter = request.form.get('chapter')
        subject = request.form.get('subject')
        if chapter:
            db.execute("INSERT INTO chapters (name,subject_id) VALUES (?,?)",[chapter,subject])
            db.commit()
            return redirect(url_for('admin'))
        return "Error: Chapter name cannot be empty",400
    db = get_database()
    # subjects = db.execute("SELECT * FROM subjects").fetchall()
    return render_template('add_chapter.html',user=user,subjects=subjects)

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        error = None
        db = get_database()
        email = request.form['email']
        username = request.form['name']
        password = request.form['password']
        role = request.form['role']
        hashed_password = generate_password_hash(password,method='pbkdf2:sha256')
        cp = request.form['confirm_password']
        pre_user = db.execute("SELECT * FROM users WHERE email = ?",[email]).fetchone()
        if not pre_user:
            if password == cp:
                db.execute("INSERT INTO users (email,name,password,role) VALUES (?,?,?,?)",[email,username,hashed_password,role])
                db.commit()
                session['user'] = email
                return render_template('login.html',error='Successfully Registered')
            else:
                return render_template('register.html',error='Password not match')
        else:
            return render_template('register.html',error='User already exist')
    else:
        return render_template('register.html')

@app.route('/logout',methods=['GET','POST'])
def logout():
    if request.method == 'POST':
        if 'user' in session:
            session.pop('user')
            session.pop('user_type')
            return redirect(url_for('home'))
        else:
            return render_template('login.html',error1='Please login first')



if __name__ == '__main__':
    app.run(debug=True)