from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from sqlalchemy import distinct
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo
# from jinja2 import render_template_string
import random
import os
os.urandom(24)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scams.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/img/'
app.config['LOGIN_REDIRECT_URL'] = '/'
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
# Define the user login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check your username and password', 'danger')
    return render_template('login.html', form=form)
# Define the login form

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')
class AdminLogin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return '<AdminLogin %r>' % self.username
# UserLogin

class UserLogin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return '<AdminLogin %r>' % self.username
# prodile Class

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Add any other fields you want to store in the user profile

class Scam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    location = db.Column(db.String(50))
    tags = db.relationship('Tag', secondary='scam_tag', backref='scams')
    images = db.relationship('Image', backref='scam', lazy=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user_login.id'))
    scam_comments = db.relationship('ScamComment', backref='scam', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='user_scams', lazy=True)
    views = db.Column(db.Integer, nullable=False, default=0)
    def __repr__(self):
        return '<Scam %r>' % self.id
class ScamComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    scam_id = db.Column(db.Integer, db.ForeignKey('scam.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user_login.id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    scam_id = db.Column(db.Integer, db.ForeignKey('scam.id'), nullable=False)
    def __repr__(self):
        return '<Image %r>' % self.filename

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user:
        raise ValidationError('That username is taken. Please choose a different one.')
def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user:
        raise ValidationError('That email is taken. Please choose a different one.')
# Blog Class
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey(
        'admin_login.id'), nullable=False)
    author = db.relationship('AdminLogin', backref='blogs')
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def edit(self, title, content):
        self.title = title
        self.content = content
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class AnonymousUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    is_anonymous = db.Column(db.Boolean, default=True)
    def __init__(self):
        self.username = f"Anonymous{random.randint(1000, 9999)}"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile = db.relationship('UserProfile', backref='user', uselist=False)
    scams = db.relationship('Scam', backref='author', lazy='dynamic')
    def __repr__(self):
        return '<User %r>' % self.username

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password')
    submit = SubmitField('Update')
# Blog posts classes
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500), nullable=True)
    author = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    likes = db.Column(db.Integer, nullable=False, default=0)
    
    comments = db.relationship('Comment', backref='post', lazy=True)
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Integer, nullable=False, default=0)
    def __repr__(self):
        return '<Tag %r>' % self.name

scam_tag = db.Table('scam_tag',
                    db.Column('scam_id', db.Integer, db.ForeignKey(
                        'scam.id'), primary_key=True),
                    db.Column('tag_id', db.Integer, db.ForeignKey(
                        'tag.id'), primary_key=True)
                    )
# Create the database tables
with app.app_context():
    db.create_all()
def time_ago(dt):
    now = datetime.utcnow()
    diff = now - dt
    total_seconds = int(diff.total_seconds())
    if total_seconds < 60:
        return f'{total_seconds} seconds ago'
    if total_seconds < 3600:
        return f'{total_seconds // 60} minutes ago'
    if total_seconds < 86400:
        return f'{total_seconds // 3600} hours ago'
    return f'{total_seconds // 86400} days ago'
# profile route
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.username != username:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.password = form.password.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html', title='Profile', form=form, user=user)
@app.route('/tags')
def get_tags():
    tags = Tag.query.all()
    return jsonify([{'id': tag.id, 'name': tag.name} for tag in tags])
@app.route('/')
def index():
    search = request.args.get('search')
    tag_id = request.args.get('tag_id')
    category = request.args.get('category')
    posts = Post.query.order_by(Post.created_on.desc()).all()
    categories = [c[0] for c in db.session.query(distinct(Scam.category)).all()]
    # Return distinct categories as JSON when requested
    if request.args.get('get_categories') == '1':
        return jsonify(categories)
    # Filter by category if a category is provided
    if category:
        scams = Scam.query.filter(Scam.category == category).order_by(Scam.date.desc()).all()
    else:
        scams = Scam.query.order_by(Scam.date.desc()).all()
    if tag_id:
        tag = Tag.query.get(tag_id)
        scams = tag.scams
    elif search:
        scams = Scam.query.filter(
            Scam.title.contains(search) |
            Scam.category.contains(search) |
            Scam.description.contains(search) |
            Scam.email.contains(search) |
            Scam.phone_number.contains(search) |
            Scam.location.contains(search) |
            Scam.tags.any(Tag.name.contains(search))
        ).all()
    tags = Tag.query.order_by(Tag.weight.desc()).all()
    if current_user.is_authenticated:
        current_user_name = current_user.username
        message = 'Welcome back, ' + current_user.username + '!'
    else:
        current_user_name = None
        message = 'Welcome! You are currently anonymous.'
        return render_template('index.html', scams=scams, tags=tags, message=message, current_user_name=current_user_name, posts=posts, search=search, categories=categories)
    search = request.args.get('search')
    tag_id = request.args.get('tag_id')
    category = request.args.get('category')
    posts = Post.query.order_by(Post.created_on.desc()).all()
    categories = [c[0] for c in db.session.query(distinct(Scam.category)).all()]
    # Return distinct categories as JSON when requested
    if request.args.get('get_categories') == '1':
        categories = [c[0] for c in db.session.query(distinct(Scam.category)).all()]
        return jsonify(categories)
    # Filter by category if a category is provided
    if category:
        scams = Scam.query.filter(Scam.category == category).order_by(Scam.date.desc()).all()
    else:
        scams = Scam.query.order_by(Scam.date.desc()).all()
    if tag_id:
        tag = Tag.query.get(tag_id)
        scams = [scam for scam in scams if scam in tag.scams]
    if search:
        scams = [scam for scam in scams if (
            search in scam.title or
            search in scam.category or
            search in scam.description or
            search in scam.email or
            search in scam.phone_number or
            search in scam.location or
            any(search in tag.name for tag in scam.tags)
        )]
    tags = Tag.query.order_by(Tag.weight.desc()).all()
    if current_user.is_authenticated:
        current_user_name = current_user.username
        message = 'Welcome back, ' + current_user.username + '!'
    else:
        current_user_name = None
        message = 'Welcome! You are currently anonymous.'
        return render_template('index.html', scams=scams, tags=tags, message=message, current_user_name=current_user_name, posts=posts, search=search, categories=categories)
    search = request.args.get('search')
    tag_id = request.args.get('tag_id')
    category = request.args.get('category')
    posts = Post.query.order_by(Post.created_on.desc()).all()
        # Return distinct categories as JSON when requested
    if request.args.get('get_categories') == '1':
        categories = [c[0] for c in db.session.query(distinct(Scam.category)).all()]
        return jsonify(categories)
    # Filter by category if a category is provided
    if category:
        scams = Scam.query.filter(Scam.category == category).order_by(Scam.date.desc()).all()
    else:
        scams = Scam.query.order_by(Scam.date.desc()).all()
    if tag_id:
        tag = Tag.query.get(tag_id)
        scams = tag.scams
    elif search:
        scams = Scam.query.filter(
            Scam.title.contains(search) |
            Scam.category.contains(search) |
            Scam.description.contains(search) |
            Scam.email.contains(search) |
            Scam.phone_number.contains(search) |
            Scam.location.contains(search) |
            Scam.tags.any(Tag.name.contains(search))
        ).all()
        # return redirect(url_for('search', search=search))
    else:
        scams = Scam.query.order_by(Scam.date.desc()).all()
    tags = Tag.query.order_by(Tag.weight.desc()).all()
    if current_user.is_authenticated:
        current_user_name = current_user.username
        message = 'Welcome back, ' + current_user.username + '!'
    else:
        current_user_name = None
        message = 'Welcome! You are currently anonymous.'
    # post_id = 0  # example
    return render_template('index.html', scams=scams, tags=tags, message=message, current_user_name=current_user_name, posts=posts, search=search, categories=categories)

@app.route('/scam', methods=['GET', 'POST'])
def scam():
    if current_user.is_authenticated:
        tags = Tag.query.all()
        # Get recent scams
        recent_scams = Scam.query.order_by(Scam.date.desc()).limit(5).all()
        # Calculate the start of the current week (Sunday)
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday() + 1)
        # Get the count of recent scams added this week
        recent_scams_count = Scam.query.filter(Scam.date >= start_of_week).count()
        recent_scams_formatted = []
        for scam in recent_scams:
            # Get the first image if available
            first_image = scam.images[0] if scam.images else None
            # Build the image URL
            image_url = url_for('static', filename=f'img/{first_image.filename}') if first_image else None
            recent_scams_formatted.append({
                'title': scam.title,
                'author': scam.user.username if scam.user else 'Anonymous',  # Use the author's username
                'image_url': image_url,  # Use the image URL
                'views': scam.views,  # Replace with the scam's view count
                # Format the date as desired
                'date_posted': scam.date.strftime('%d %b %Y'),
                'time_ago': time_ago(scam.date),
            })
        if request.method == 'POST':
            title = request.form['title']
            category = request.form['category']
            description = request.form['description']
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            location = request.form.get('location')
            user_id = current_user.id
            tag_names = request.form.get('tags', '').split(',')
            tags = []
            for name in tag_names:
                name = name.strip()
                if name:
                    tag = Tag.query.filter_by(name=name).first()
                    if not tag:
                        tag = Tag(name=name)
                        db.session.add(tag)
                    tags.append(tag)
            scam = Scam(title=title, category=category, description=description, email=email,
                        phone_number=phone_number, location=location, tags=tags, user_id=current_user.id)
            # Save uploaded images
            images = request.files.getlist('images')
            for image in images:
                filename = secure_filename(image.filename)
                if filename:
                    file_path = os.path.join(
                        app.config['UPLOAD_FOLDER'], filename)
                    image.save(file_path)
                    new_image = Image(filename=filename, scam=scam)
                    db.session.add(new_image)
                # Get 
            db.session.add(scam)
            db.session.commit()
            flash('Your scam has been added!', 'success')
            return redirect(url_for('index'))
        return render_template('scam.html', tags=tags, recent_scams=recent_scams_formatted, recent_scams_count=recent_scams_count)
    else:
        # User is anonymous
        tags = Tag.query.all()
        if request.method == 'POST':
            title = request.form['title']
            category = request.form['category']
            description = request.form['description']
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            location = request.form.get('location')
            user_id = current_user.id
            tag_names = request.form.get('tags', '').split(',')
            tags = []
            for name in tag_names:
                name = name.strip()
                if name:
                    tag = Tag.query.filter_by(name=name).first()
                    if not tag:
                        tag = Tag(name=name)
                        db.session.add(tag)
                    tags.append(tag)
            scam = Scam(title=title, category=category, description=description, email=email,
                        phone_number=phone_number, location=location, tags=tags, user_id=current_user.id)
            # Save uploaded images
            images = request.files.getlist('images')
            for image in images:
                filename = secure_filename(image.filename)
                if filename:
                    file_path = os.path.join(
                        app.config['UPLOAD_FOLDER'], filename)
                    image.save(file_path)
                    new_image = Image(filename=filename, scam=scam)
                    db.session.add(new_image)
            db.session.add(scam)
            db.session.commit()
            flash('Your scam has been added!', 'success')
            return redirect(url_for('index'))
        
# Add new scam as anonymous
        return render_template('anonymous_scam.html', tags=tags)

@app.route('/scam/<int:scam_id>')
def scam_detail(scam_id):
    scam = Scam.query.get_or_404(scam_id)
    scam.views += 1
    db.session.commit()
    return render_template('scam_detail.html', scam=scam)
@app.route('/scam/<int:scam_id>/add_scam_comment', methods=['POST'])
def add_scam_comment(scam_id):
    if current_user.is_authenticated:
        content = request.form['content']
        scam_comment = ScamComment(content=content, scam_id=scam_id, user_id=current_user.id)
        db.session.add(scam_comment)
        db.session.commit()
        flash('Your scam comment has been added!', 'success')
    else:
        flash('You must be logged in to add a scam comment.', 'warning')
    return redirect(url_for('scam_detail', scam_id=scam_id))
# Anon
@app.route('/user/login/anonymous', methods=['GET'])
def user_login_anonymous():
    anonymous_user = AnonymousUser()
    db.session.add(anonymous_user)
    db.session.commit()
    login_user(anonymous_user)
    return redirect(url_for('index'))

# Initialize the Flask-Login extension
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        return user
    else:
        return AnonymousUser.query.get(int(user_id))

# @login_manager.user_loader
# def load_user(user_id):
#     user = User.query.options(joinedload(User.profile)).get(int(user_id))
#     if user is not None:
#         return user
#     else:
#         return AdminLogin.query.get(int(user_id))

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))  # <-- redirect to the main page
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_login = AdminLogin.query.filter_by(username=username).first()
        if admin_login and admin_login.password == password:
            login_user(admin_login)
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin():
    scams = Scam.query.all()
    return render_template('admin.html', scams=scams)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/scams')
@login_required
def admin_scams():
    scams = Scam.query.all()
    return render_template('admin_scams.html', scams=scams)

@app.route('/admin/scams/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_scam(id):
    scam = Scam.query.get_or_404(id)
    if request.method == 'POST':
        scam.title = request.form['title']
        scam.category = request.form['category']
        scam.description = request.form['description']
        scam.email = request.form.get('email')
        scam.phone_number = request.form.get('phone_number')
        scam.location = request.form.get('location')
        tag_names = request.form.get('tags', '').split(',')
        tags = []
        for name in tag_names:
            name = name.strip()
            if name:
                tag = Tag.query.filter_by(name=name).first()
                if not tag:
                    tag = Tag(name=name)
                    db.session.add(tag)
                tags.append(tag)
        scam.tags = tags
        images = request.files.getlist('images')
        for image in images:
            if image.filename:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                scam_image = Image(filename=filename, scam_id=scam.id)
                db.session.add(scam_image)
        db.session.commit()
        flash('Scam updated successfully')
        return redirect(url_for('admin_scams'))
    tags = Tag.query.all()
    return render_template('edit_scam.html', scam=scam, tags=tags)

@app.route('/admin/scams/delete/int:id', methods=['POST'])
@login_required
def delete_scam(id):
    scam_id = request.form['scam_id']
    scam = Scam.query.get_or_404(id)
    db.session.delete(scam)
    db.session.commit()
    flash('Scam deleted successfully')
    return redirect(url_for('admin_scams'))

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/trending_scams')
def trending_scams():
    return render_template('trending_scams.html')
# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        profile = UserProfile(
            user_id=user.id, username=form.username.data, email=form.email.data)
        db.session.add(profile)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#Blog posts
@app.route('/post/new', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        image = request.form['image']
        author = request.form['author']
        new_post = Post(title=title, body=body, image=image, author=author)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('pagination', page_num=1))
    return render_template('new_post.html')
@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        # Update the post with the new data
        post.title = request.form['title']
        post.body = request.form['body']
        # Add other fields if necessary
        
        db.session.commit()
        return redirect(url_for('view_post', post_id=post.id))
    
    return render_template('edit_post.html', post=post)
@app.route('/all_posts')
def all_posts():
    posts = Post.query.all()  # Retrieve all posts from your database
    return render_template('all_posts.html', posts=posts)
@app.route('/view_post/<int:post_id>', methods=['GET'])
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('view_post.html', post=post)
# Remove the duplicate route here
@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    body = data['body']
    author = data['author']
    new_comment = Comment(body=body, author=author, post=post)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({"body": body, "author": author})
@app.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    post_data = {
        'id': post.id,
        'title': post.title,
        'body': post.body,
        'author': post.author,
        'created_on': post.created_on.strftime('%Y-%m-%d %H:%M:%S'),
        'image': post.image,
        'likes': post.likes,
        'comments': [
            {
                'body': comment.body,
                'author': comment.author
            } for comment in post.comments
        ]
    }
    return jsonify(post_data)

@app.route('/post/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(request.referrer)
@app.route('/search')
def search():
    keyword = request.args.get('search')
    scams = Scam.query.filter(Scam.title.contains(keyword)).all()
    posts = Post.query.filter(Post.title.contains(keyword)).all()
    return render_template('search.html', scams=scams, posts=posts, keyword=keyword)
@app.route('/page/<int:page_num>')
def pagination(page_num):
    per_page = 3
    posts = Post.query.order_by(Post.created_on.desc()).paginate(page=page_num, per_page=per_page)
    return render_template('pagination.html', posts=posts)
@app.route('/all_posts_api')
def all_posts_api():
    posts = Post.query.all()
    posts_json = [
        {
            'title': post.title,
            'body': post.body,
            'image': post.image,
            'author': post.author,
            'created_on': post.created_on.isoformat(),
            'likes': post.likes,
            'comments': len(post.comments)
        }
        for post in posts
    ]
    return jsonify(posts_json)
# Blogs
@app.route('/blogs')
def blogs():
    blogs = Blog.query.order_by(Blog.date.desc()).all()
    return render_template('blogs.html', blogs=blogs)

@app.route('/blog/<int:id>')
def blog_detail(id):
    blog = Blog.query.get_or_404(id)
    return render_template('blog_detail.html', blog=blog)

@app.route('/blog/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_blog(id):
    blog = Blog.query.get_or_404(id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        blog.edit(title, content)
        flash('Your post has been updated!', 'success')
        return redirect(url_for('blog_detail', id=blog.id))
    return render_template('edit_blog.html', blog=blog)

@app.route('/blog/<int:id>/delete', methods=['POST'])
@login_required
def delete_blog(id):
    blog = Blog.query.get_or_404(id)
    db.session.delete(blog)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('blogs'))

if __name__ == '__main__':
    app.run(debug=True)