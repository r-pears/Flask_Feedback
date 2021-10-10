"""Feedback-Flask App Routes."""
from flask import Flask, render_template, session, redirect
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///flask-feedback"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "oh-so-secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route('/')
def homepage():
    """Redirects the user to register page."""
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a user, show a form and handle form submission."""
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.commit()
        session['username'] = user.username

        return redirect(f"/users/{user.username}")

    else:
        return render_template('users/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Show login form and handle form submission."""
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ['Invalid username/password']
            return render_template('users/login.html', form=form)

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Log out a user."""
    session.pop('username')
    return redirect('/login')


@app.route('/users/<username>')
def show_user(username):
    """Show page for logged in user."""
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    form = DeleteForm()
    user = User.query.get(username)

    return render_template('users/show.html', user=user, form=form)


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete a user and redirect to login."""
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect('/login')


@app.route('/users/<username>/feedback/new', methods=['GET', 'POST'])
def add_feedback(username):
    """Show a form to add new feedback and handle form submission."""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        new_feedback = Feedback(title=title, content=content, username=username)
        db.session.add(new_feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template('feedback/new.html', form=form)
