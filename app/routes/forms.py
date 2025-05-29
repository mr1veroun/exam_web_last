from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectMultipleField, FileField, SubmitField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, NumberRange
from app.models import Genre

class ReviewForm(FlaskForm):
    rating = SelectField(
        'Оценка',
        choices=[
            (5, 'отлично'),
            (4, 'хорошо'),
            (3, 'удовлетворительно'),
            (2, 'неудовлетворительно'),
            (1, 'плохо'),
            (0, 'ужасно')
        ],
        coerce=int,
        default=5,
        validators=[DataRequired()]
    )
    text = TextAreaField('Текст рецензии', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Повторите пароль', validators=[
        DataRequired(), EqualTo('password', message='Пароли должны совпадать')
    ])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    first_name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество')
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Пользователь с таким логином уже существует.')


class BookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Краткое описание', validators=[DataRequired()])
    year = IntegerField('Год', validators=[DataRequired(), NumberRange(min=0, max=2100)])
    publisher = StringField('Издательство', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    pages = IntegerField('Объем (в страницах)', validators=[DataRequired(), NumberRange(min=1)])
    genres = SelectMultipleField('Жанры', coerce=int, validators=[DataRequired()])
    cover = FileField('Обложка', validators=[DataRequired()])
    submit = SubmitField('Сохранить')