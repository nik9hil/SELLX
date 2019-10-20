#Importing Dependencies
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, DataRequired 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os.path
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import desc


app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
db_path = os.path.join(os.path.dirname(__file__),'database.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Defining the tables
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    def __repr__(self):
        return f"User('{self.id}','{self.username}','{self.email}')"

class NewPost(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(15))
    caption = db.Column(db.String(1000))
    message = db.Column(db.String(100))
    def __repr__(self):
        return f"NewPost('{self.id}','{self.caption}','{self.message}')"


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4,max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6,max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])
    re_password = PasswordField('re_password', validators=[InputRequired(), Length(min=6,max=80)])
    submit = SubmitField('Sign Up')
	
class NewPostForm(FlaskForm):
    Caption = StringField('Caption', validators=[InputRequired()])
    message = StringField('Message', validators=[InputRequired()], render_kw = {'rows':7})


#Login
@app.route('/index/', methods=['GET','POST'])
def index():
    return render_template('index.html',title="Index")

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                #return redirect(url_for('welcome'))
                login_user(user, remember=form.remember.data)

                return redirect(url_for('index'))
    return render_template('login.html',title="Log In",form = form)


#SignUp
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data == form.re_password.data:
        #print(form.email.data)
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            if User.query.filter_by(username=form.username.data).first() == form.username.data:
                flash("Username already exits!")
        # else:
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('index'))
    return render_template('register.html',title="Sign Up", form=form)

#LogOut
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route("/")
@app.route('/welcome')
@login_required
def welcome():
    return render_template('hello.html')


#Feeds
@app.route("/feeds")
@login_required
def getFeeds():
    options = [
    {"name":"Log out","selected":False,"link":url_for("logout")},
    {"name":"Feed","selected":True,"link":url_for("getFeeds")},
    {"name":"My Profile","selected":False,"link":url_for("getProfile")},
    #{"name":"My Network","selected":False,"link":url_for("getFriends")},
    {"name":"New Post","selected":False,"link":url_for("newPost")}
    ]

    return render_template("feed.html",title="Feed", nav_options = options ,Post_data = NewPost.query.order_by(desc(NewPost.id)).all())


#Profiles Page
@app.route("/profile")
@login_required
def getProfile():
    options = [
    {"name":"Log out","selected":False,"link":url_for("logout")},
    {"name":"Feed","selected":False,"link":url_for("getFeeds")},
    {"name":"My Profile","selected":True,"link":url_for("getProfile")},
    #{"name":"My Network","selected":False,"link":url_for("getFriends")},
    {"name":"New Post","selected":False,"link":url_for("newPost")}
    ]
    return render_template("profile.html",title="Profile",nav_options= options)


#newPost
@app.route("/post/new/",methods = ['GET','POST'])
@login_required
def newPost():
    options = [
    {"name":"Log out","selected":False,"link":url_for("logout")},
    {"name":"Feed","selected":False,"link":url_for("getFeeds")},
    {"name":"My Profile","selected":False,"link":url_for("getProfile")},
    #{"name":"My Network","selected":False,"link":url_for("getFriends")},
    {"name":"New Post","selected":True,"link":url_for("newPost")}
    ]
    form = NewPostForm()
    if form.validate_on_submit():
        user = current_user.username
        caption = form.Caption.data
        message = form.message.data

        new_post = NewPost(username=user, caption=caption, message=message)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('getFeeds'))
    return render_template("newpost.html",form=form,title="New Post",nav_options= options)



if __name__=='__main__':
	app.run(debug=True)
