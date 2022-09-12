#from curses import flash
from turtle import title
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from flask_ckeditor import CKEditor

app = Flask(__name__)

ckeditor = CKEditor(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:OPEyemi2001@localhost/our_users'

app.config['SECRET_KEY'] = "secret"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

#create a blog post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))

#create users model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='poster')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.name
    
#create form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash =PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match')])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")
class PasswordForm(FlaskForm):
    email = StringField("What's your email?", validators=[DataRequired()])
    password_hash = PasswordField("What's your password?", validators=[DataRequired()])
    submit = SubmitField("Submit")
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("content", validators=[DataRequired()], widget=TextArea())
    author = StringField("author")
    slug = StringField("slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

# login form
class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("submit")

# all posts
@app.route('/')
def index():
    flash("Welcome to our website!")
    posts = Post.query.order_by(Post.date_posted)
    return render_template('index.html', post=posts)

#login user
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successful!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password, Try Again!")
        else:
            flash("That user does not exist, Try Again!")

    return render_template('login.html', form=form)

# logout 
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have logged out!")
    return redirect(url_for('login'))

#dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("user updated successfully!")
            return render_template("dashboard.html", form=form, name_to_update = name_to_update)
        except:
            flash("Error! try again later")
            return render_template("dashboard.html", form=form, name_to_update = name_to_update)
    else:
        return render_template("dashboard.html", form=form, name_to_update = name_to_update, id = id)

    return render_template('dashboard.html')

# individual post
@app.route('/posts/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", post=post)

# add post page
@app.route("/add-post", methods=["GET", "POST"])
#@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Post(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        #form.author.data = ''
        form.slug.data = ''

        db.session.add(post)
        db.session.commit()

        flash("post submitted successfully!")

    return render_template("add_post.html", form=form)

#update post
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    posts = Post.query.order_by(Post.date_posted)
    post = Post.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        #post.author = form.author.data
        form.slug = form.slug.data
        form.content = form.content.data

        db.session.add(post)
        db.session.commit()
        flash("Post updated successfully!")
        return redirect(url_for('post', id=post.id))

    if current_user.id == post.poster_id:
        form.title.data = post.title
        #form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template("edit_post.html", form=form)

    else:
        flash("You aren't authorized to edit this post!")
        return render_template('index.html', post=posts)

# delete post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id)
    id = current_user.id

    if id == post_to_delete.poster.id:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash.info("Post deleted successfully")
            posts = Post.query.order_by(Post.date_posted)
            return render_template('index.html', post=posts)
    
        except:
            flash("Whoops! Something went wrong, please try again later")
            posts = Post.query.order_by(Post.date_posted)
            return render_template('index.html', post=posts)

    else:
        flash("You aren't authorized to delete this post!")
        posts = Post.query.order_by(Post.date_posted)
        return render_template('index.html', post=posts)

# delete user
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("user deleted successfully!!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", form=form, name=name, our_users=our_users)

    except:
        flash("Whoops! Something went wrong, please try again later...")
        return render_template("add_user.html", form=form, name=name, our_users=our_users)


#update user record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("user updated successfully!")
            return render_template("update.html", form=form, name_to_update = name_to_update)
        except:
            flash("Error! try again later")
            return render_template("update.html", form=form, name_to_update = name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update = name_to_update, id = id)

# add user
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, username=form.username.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''

        flash("User Added successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

# invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# Create Password Test Page
@app.route('/testpw', methods=['GET', 'POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()

	# Validate Form
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		# Clear the form
		form.email.data = ''
		form.password_hash.data = ''

		# Lookup User By Email Address
		pw_to_check = Users.query.filter_by(email=email).first()
		
		# Check Hashed Password
		passed = check_password_hash(pw_to_check.password_hash, password)

	return render_template("testpw.html", 
		email = email,
		password = password,
		pw_to_check = pw_to_check,
		passed = passed,
		form = form)


#create name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("form successfully submitted!")

    return render_template("name.html", 
        name = name, 
        form = form)

if __name__ == '__main__':
    app.run(debug=True)