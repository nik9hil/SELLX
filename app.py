#Importing Dependencies
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, FileField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os.path
from os import urandom
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
    name = db.Column(db.String(20))
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    posts = db.relationship('NewPost', backref='author',lazy=True)
    def __repr__(self):
        return f"User('{self.id}','{self.username}','{self.email}')"

class NewPost(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key = True)
    description = db.Column(db.String(1000))
    tag = db.Column(db.String(30))
    sub_tag = db.Column(db.String(40))
    price = db.Column(db.Integer) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    img = db.Column(db.String(200), nullable = False)
    loc = db.Column(db.String(20))
    def __repr__(self):
        return f"NewPost('{self.id}','{self.tag}','{self.sub_tag}','{self.description}','{self.price},'{self.user_id},'{self.img}','{self.loc}')"

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4,max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6,max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    name = StringField('name', validators=[InputRequired()])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])
    re_password = PasswordField('re_password', validators=[InputRequired(), Length(min=6,max=80)])
    submit = SubmitField('Sign Up')
	
class NewPostForm(FlaskForm):
    tag = StringField('Tag', validators=[InputRequired()])
    sub_tag = StringField('SubTag', validators=[InputRequired()])
    description = StringField('Description', validators=[InputRequired()])
    price = StringField('Price', validators=[InputRequired()])
    img = FileField('Image')
    loc = StringField('Location', validators=[InputRequired()])
    submit = SubmitField('Post!')


@app.route('/', methods=['GET','POST'])
def star():
    fur = NewPost.query.filter(NewPost.tag=='Furniture').count()
    car = NewPost.query.filter(NewPost.tag=='Car').count()
    ele = NewPost.query.filter(NewPost.tag=='Electronics').count()
    books = NewPost.query.filter(NewPost.tag=='Books & Magazine').count()
    other = NewPost.query.filter(NewPost.tag=='Other').count()
    watch = NewPost.query.filter(NewPost.tag=='Watch').count()
    return render_template('index.html',title="Index",Post_data = NewPost.query.all(), fcnt=fur, carcnt=car, elcnt = ele, bcnt= books, ocnt = other, wcnt= watch)

@app.route('/index/', methods=['GET','POST'])
@login_required
def index():
    fur = NewPost.query.filter(NewPost.tag=='Furniture').count()
    car = NewPost.query.filter(NewPost.tag=='Car').count()
    ele = NewPost.query.filter(NewPost.tag=='Electronics').count()
    books = NewPost.query.filter(NewPost.tag=='Books & Magazine').count()
    other = NewPost.query.filter(NewPost.tag=='Other').count()
    watch = NewPost.query.filter(NewPost.tag=='Watch').count()
    return render_template('index.html',title="Index",Post_data = NewPost.query.all(), fcnt=fur, carcnt=car, elcnt = ele, bcnt= books, ocnt = other, wcnt= watch)

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
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password,name = form.name.data)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('index'))
    return render_template('register.html',title="Sign Up", form=form)


def save_picture(form_picture):
    random_hex = urandom(8).hex()
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static\media', picture_fn)
    form_picture.save(picture_path)

    return picture_path

#newPost
@app.route("/new/",methods = ['GET','POST'])
@login_required
def new():
    form = NewPostForm()
    if form.validate_on_submit():
        print(form.tag.data)
        user = current_user.id
        descrp = form.description.data
        tagl = form.tag.data
        stag = form.sub_tag.data
        amt = form.price.data
        lo = form.loc.data
        image = save_picture(form.img.data)
        print(image)
        new_post = NewPost(description=descrp, tag=tagl,sub_tag=stag, price=amt, user_id=user, img=image,loc = lo)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("posting.html",form=form,title="New Post")

#Profiles Page
@app.route("/profile")
@login_required
def getProfile():
    return render_template("profile.html",title="Profile")

@app.route("/singlelist/")
@login_required
def singlelist():
    return render_template("listings-single.html",title="Feed")#,Post_data = NewPost.query.filter(NewPost.id==postid))


#LogOut
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))
if __name__=='__main__':
	app.run(debug=True)
