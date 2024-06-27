from flask import render_template, url_for, flash, redirect, request, abort, make_response
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, NoteForm
from app.models import User, Note, Session
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
import secrets


@app.before_request
def load_user_from_cookie():
    if not current_user.is_authenticated:
        session_token = request.cookies.get('session_token')
        if session_token:
            session = Session.query.filter_by(session_token=session_token).first()
            if session and session.expiry_date > datetime.utcnow():
                user = User.query.get(session.user_id)
                if user:
                    login_user(user)


@app.route("/")
@app.route("/home")
@login_required
def home():
    notes = Note.query.filter_by(owner=current_user)
    return render_template('index.html', notes=notes)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            remember_me = form.remember_me.data
            if remember_me:
                return create_session(user, remember_me)
            else:
                login_user(user)
                response = make_response(redirect(url_for('home')))
                return response
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


def create_session(user, remember_me):
    token = secrets.token_hex(16)
    expiry_date = datetime.utcnow() + timedelta(days=30 if remember_me else 0)
    new_session = Session(user_id=user.id, session_token=token, expiry_date=expiry_date)
    db.session.add(new_session)
    db.session.commit()

    response = make_response(redirect(url_for('home')))
    if remember_me:
        response.set_cookie('session_token', token, expires=expiry_date)
    else:
        response.set_cookie('session_token', token)  # No expiry for session cookie
    return response


@app.route("/logout")
def logout():
    session_token = request.cookies.get('session_token')
    if session_token:
        session = Session.query.filter_by(session_token=session_token).first()
        if session:
            db.session.delete(session)
            db.session.commit()

    response = make_response(redirect(url_for('login')))
    response.delete_cookie('session_token')
    logout_user()
    return response


@app.route("/note/new", methods=['GET', 'POST'])
@login_required
def new_note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(title=form.title.data, content=form.content.data, owner=current_user)
        db.session.add(note)
        db.session.commit()
        flash('Your note has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_note.html', title='New Note', form=form)


@app.route("/note/delete/<int:note_id>", methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.owner != current_user:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    flash('Your note has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/note/edit/<int:note_id>", methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.owner != current_user:
        abort(403)
    form = NoteForm()
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        db.session.commit()
        flash('Your note has been updated!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = note.title
        form.content.data = note.content
    return render_template('create_note.html', title='Edit Note', form=form, legend='Edit Note')
