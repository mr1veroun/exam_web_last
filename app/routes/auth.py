from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.routes.forms import LoginForm
from app.routes.forms import RegistrationForm
from app.models import db, User, Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            error = 'Невозможно аутентифицироваться с указанными логином и паролем'
            flash(error, 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # По умолчанию назначаем роль "Пользователь"
        user_role = Role.query.filter_by(name='Пользователь').first()
        if not user_role:
            flash('Роль "Пользователь" не найдена. Обратитесь к администратору.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            role_id=user_role.id
        )
        try:
            db.session.add(user)
            db.session.commit()
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            login_user(user)
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при регистрации. Попробуйте ещё раз.', 'danger')
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.', 'success')
    return redirect(url_for('main.index'))