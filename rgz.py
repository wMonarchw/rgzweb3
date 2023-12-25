from flask import Blueprint, redirect, url_for, render_template, request, session, current_app, flash
from Db import db
from Db.models import users, profiles
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
import os


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

rgz = Blueprint('rgz', __name__)



@rgz.route('/')
@rgz.route('/index')
def start():
    return redirect('/rgz/', code=302)

@rgz.route('/rgz/')
def main():
    return render_template('rgz.html')

@rgz.route('/rgz/login', methods=['GET', 'POST'])
def login():
    errors = []
    if request.method == 'GET':
        return render_template('login.html')

    username_form = request.form.get('username')
    password_form = request.form.get('password')

    my_user = users.query.filter_by(username=username_form).first()

    if my_user is not None:
        if check_password_hash(my_user.password, password_form):
            login_user(my_user, remember = False)
            return redirect('/rgz/glav')
        else: 
            errors.append("Неправильный пароль")
            return render_template('login.html', errors=errors)
        
    if not (username_form or password_form):
        errors.append("Пожалуйста заполните все поля")
        return render_template("login.html", errors=errors)
    if username_form == '':
        errors.append("Пожалуйста заполните все поля")
        print(errors)
        return render_template('login.html', errors=errors)
    if password_form == '':
        errors.append("Пожалуйста заполните все поля")
        print(errors)
        return render_template('login.html', errors=errors)
    else: 
        errors.append('Пользователя не существует')
        return render_template('login.html', errors=errors)
    

@rgz.route('/rgz/register', methods=['GET', 'POST'])
def handle_register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        gender = request.form.get('gender')
        partner_gender = request.form.get('partner_gender')
        age = request.form.get('age')
        description = request.form.get('description')
        file = request.files.get('file')

        errors = []

        if not (username and password and name and gender and partner_gender and age and description and file):
            errors.append("Пожалуйста, заполните все поля")

        if len(password) < 5:
            errors.append("Пароль должен быть не менее 5 символов")

        hash_password = generate_password_hash(password)

        existing_user = users.query.filter_by(username=username).first()
        if existing_user:
            errors.append("Пользователь с данным именем уже существует")

        new_user = users(username=username, password=hash_password)
        db.session.add(new_user)
        db.session.commit()

        user_id = new_user.user_id

        new_profile = profiles(user_id=user_id, age=age, name=name, gender=gender, searching_for=partner_gender, about_me=description)
        db.session.add(new_profile)
        db.session.commit()

        # Загрузка файла
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            new_profile.photo = file_path
            db.session.commit()

        # Возвращаем успешный результат
        return redirect('/rgz/glav')

    return render_template('register.html')


@rgz.route('/rgz/profile/')
@login_required
def profile():
    user_id = current_user.user_id

    profile = profiles.query.filter_by(user_id=user_id).first()
    if not profile:
        return redirect('/rgz/login')

    age = profile.age
    name = profile.name
    gender = profile.gender
    gender_search = profile.searching_for
    about_me = profile.about_me
    photo = profile.photo
    photo_url = url_for('static', filename=os.path.join('uploads', os.path.basename(photo)).replace('\\', '/'), _external=True)

    return render_template('profile.html', age=age, name=name, gender=gender, gender_search=gender_search, about_me=about_me, photo=photo, photo_url=photo_url)

@rgz.route('/rgz/profile/change/', methods=['GET', 'POST'])
@login_required
def profile_change():
    user_id = current_user.user_id
    if user_id is None:
        return redirect('/rgz/login')
    
    errors = []
    if request.method == "GET":
        return render_template('change.html', errors=errors)

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            profile = profiles.query.filter_by(user_id=user_id).first()
            profile.photo = file_path
            db.session.commit()
            
            return redirect('/rgz/profile')
    
    description = request.form.get("description")
    name = request.form.get('name')
    gender = request.form.get("gender")
    partner_gender = request.form.get("partner_gender")
    age = request.form.get('age')
    hide_profile = request.form.get('hide_profile')
    
    profile = profiles.query.filter_by(user_id=user_id).first()
    current_age = profile.age
    current_name = profile.name
    current_gender = profile.gender
    current_searching_for = profile.searching_for
    current_about_me = profile.about_me
    current_hide_profile = profile.hide_profile
    
    age = current_age if age == '' else int(age)
    name = name if name else current_name
    gender = gender if gender else current_gender
    partner_gender = partner_gender if partner_gender else current_searching_for
    description = description if description else current_about_me
    hide_profile = bool(hide_profile) if hide_profile else current_hide_profile
    
    profile.age = age
    profile.name = name
    profile.gender = gender
    profile.searching_for = partner_gender
    profile.about_me = description
    profile.hide_profile = hide_profile

    db.session.commit()
    
    return redirect('/rgz/profile')

@rgz.route('/rgz/profile/delete/', methods=['GET', 'POST'])
@login_required
def profile_delete():
    user_id = session.get('id')

    if user_id is None:
        return redirect('/rgz/login')

    profile = profiles.query.filter_by(user_id=user_id).first()
    user = users.query.filter_by(user_id=user_id).first()

    db.session.delete(profile)
    db.session.delete(user)
    db.session.commit()

    session.clear()

    flash("Ваш профиль был успешно удален")
    return redirect('/rgz/')

@rgz.route('/rgz/glav', methods=['GET', 'POST'])
@login_required
def glav():
    user_id = current_user.user_id
    user = current_user
    if user_id is None:
        return redirect('/rgz/login')

    search_name = request.args.get('search_name')
    search_age = request.args.get('search_age')
    page = request.args.get('page', 1, type=int)

    user = users.query.get(user_id)
    if user is None:
        flash("Профиль не найден.")
        return redirect('/rgz/profile')

    query = profiles.query.filter(db.or_(profiles.hide_profile == False, profiles.hide_profile == None))
    if search_name:
        query = query.filter(profiles.name.ilike(f"%{search_name}%"))
    if search_age:
        query = query.filter(profiles.age == search_age)

    user_profiles = profiles.query.filter_by(user_id=user.user_id).all()
    user_profile = user_profiles[0]
    if user_profile.searching_for == 'male' and user_profile.gender == 'female':
        query = query.filter(profiles.gender == 'male', profiles.searching_for == 'female')
    elif user_profile.searching_for == 'male' and user_profile.gender == 'male':
        query = query.filter(profiles.gender == 'male', profiles.searching_for == 'male')
    elif user_profile.searching_for == 'female' and user_profile.gender == 'male':
        query = query.filter(profiles.gender == 'female', profiles.searching_for == 'male')
    elif user_profile.searching_for == 'female' and user_profile.gender == 'female':
        query = query.filter(profiles.gender == 'female', profiles.searching_for == 'female')


    offset = (page - 1) * 3
    query = query.offset(offset).limit(3)
    search_results = query.all()

    results_with_photos = []
    for result in search_results:
        photo_filename = result.photo
        if photo_filename:
            photo_url = url_for('static', filename=os.path.join('uploads', os.path.basename(photo_filename)).replace('\\', '/'), _external=True)
        else:
            photo_url = None
        results_with_photos.append((result.user_id, result.age, result.name, result.gender, result.searching_for, result.about_me, photo_url))

    next_url = url_for('rgz.glav', page=page+1, search_name=search_name, search_age=search_age) \
        if len(search_results) == 3 else None
    prev_url = url_for('rgz.glav', page=page-1, search_name=search_name, search_age=search_age) \
        if page > 1 else None

    return render_template('glav.html', search_results=results_with_photos, next_url=next_url, prev_url=prev_url)
    
@rgz.route('/rgz/logout')
@login_required
def logout():
    session.clear()
    return render_template('rgz.html')