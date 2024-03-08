from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, bcrypt
from app.models import User, Movie, feedback
from app.forms import RegisterForm, LoginForm, EditProfileForm, AddReviewForm, ViewReviewForm
from sqlalchemy import text

def fix_name(name):
    name = name.lower()
    return ' '.join(name.split())

@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user.')
        return redirect(url_for('home'))
    return render_template('register.html', form=form, title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))
    return render_template('login.html', form=form, title='Sign In')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.email)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('home'))
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    return render_template('edit_profile.html', form=form, title='Edit Profile')

@app.route('/add_review', methods=['GET', 'POST'])
@login_required
def add_review():
    form = AddReviewForm()
    if form.validate_on_submit():
        movie_name = form.movie_name.data
        movie_name = fix_name(movie_name)
        movie = Movie.query.filter_by(name=movie_name).first()
        
        if movie is None:
            movie = Movie(name=movie_name)
            db.session.add(movie)
        
        review_text = form.review.data
        current_user.reviewed.append(movie)
        
        feedback_entry = feedback.insert().values(user_id=current_user.id, movie_id=movie.id, review=review_text)
        db.session.execute(feedback_entry)
        db.session.commit()
        
        flash('Review Added successfully.')
        return redirect(url_for('home'))
    
    return render_template('add_review.html', form=form, title='Add Review')


@app.route('/view_review', methods=['GET', 'POST'])
@login_required
def view_review():
    form = ViewReviewForm()
    if form.validate_on_submit():
        return redirect(url_for('review', movie_name=form.movie_name.data))
    return render_template('view_review.html', form=form, title='View Review')

@app.route('/review/<movie_name>')
@login_required
def review(movie_name):
    movie_name = fix_name(movie_name)
    movie = Movie.query.filter_by(name=movie_name).first()
    
    if movie:
        sql_query = text(
            "SELECT u.name as name, f.review as review FROM user u "
            "JOIN feedback f ON u.id = f.user_id "
            "WHERE f.movie_id = :movie_id AND f.review is not NULL"
        )
        all_reviews = db.session.execute(sql_query, {'movie_id': movie.id}).fetchall()
        return render_template('review.html', title='Review', movie=movie.name, reviews=all_reviews)
    else:
            flash(f'Movie does not exist in the database. Add a review about {movie_name}.')
            return redirect(url_for('view_review'))
