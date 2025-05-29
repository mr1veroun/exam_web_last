from flask import (
    request, redirect, url_for, flash, Blueprint, render_template, abort, current_app, session
)
from flask_login import login_required, current_user
import os
import hashlib
from werkzeug.utils import secure_filename
from markdown import markdown
import bleach
from datetime import datetime, date
from app.models import db, Book, Review, Cover, Genre
from app.routes.forms import ReviewForm, BookForm
from app.models import BookView


books_bp = Blueprint('books', __name__)

# Настройки bleach для безопасного HTML из Markdown
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li',
    'ol', 'strong', 'ul', 'p', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'br', 'hr'
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'abbr': ['title'],
    'acronym': ['title'],
}



@books_bp.route('/book/<int:book_id>')
def view_book(book_id):
    book = Book.query.get_or_404(book_id)

    # --- Учёт просмотров книги (ограничение 10 в день на пользователя/гостя) ---
    user = current_user if current_user.is_authenticated else None
    session_id = session.get('sid')
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        session['sid'] = session_id

    

    today = date.today()
    view_count_query = BookView.query.filter(
        BookView.book_id == book.id,
        BookView.viewed_at >= datetime(today.year, today.month, today.day)
    )
    if user:
        view_count_query = view_count_query.filter(BookView.user_id == user.id)
    else:
        view_count_query = view_count_query.filter(BookView.session_id == session_id)

    if view_count_query.count() < 10:
        db.session.add(BookView(
            book_id=book.id,
            user_id=user.id if user else None,
            session_id=None if user else session_id
        ))
        db.session.commit()

    # --- Markdown + bleach для описания ---
    raw_html = markdown(book.description or "")
    safe_html = bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)

    # --- Получение рецензий ---
    reviews = Review.query.filter_by(book_id=book.id).order_by(Review.created_at.desc()).all()
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(book_id=book.id, user_id=current_user.id).first()

    return render_template(
        'book_detail.html',
        book=book,
        description_html=safe_html,
        reviews=reviews,
        user_review=user_review
    )


# Просмотр книги
# @books_bp.route('/book/<int:book_id>')
# def view_book(book_id):
#     book = Book.query.get_or_404(book_id)
#     raw_html = markdown(book.description)
#     safe_html = bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
#     reviews = Review.query.filter_by(book_id=book.id).order_by(Review.created_at.desc()).all()
#     return render_template(
#         'book_detail.html',
#         book=book,
#         description_html=safe_html,
#         reviews=reviews
#     )

# Удаление книги
@books_bp.route('/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if current_user.role.name != 'Администратор':
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('main.index'))
    try:
        # Удаляем файл обложки из файловой системы
        if book.cover:
            cover_path = os.path.join(current_app.root_path, 'static', 'covers', book.cover.filename)
            if os.path.exists(cover_path):
                os.remove(cover_path)
        # Удаляем книгу (каскадно удалятся рецензии, обложка, связи с жанрами)
        db.session.delete(book)
        db.session.commit()
        flash('Книга и все связанные данные успешно удалены.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при удалении книги: {e}")
        flash('Ошибка при удалении книги.', 'danger')
    return redirect(url_for('main.index'))


@books_bp.route('/book/<int:book_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    existing_review = Review.query.filter_by(book_id=book.id, user_id=current_user.id).first()
    if existing_review:
        flash('Вы уже оставили рецензию на эту книгу.', 'warning')
        return redirect(url_for('books.view_book', book_id=book.id))
    if current_user.role.name not in ['Пользователь', 'Модератор', 'Администратор']:
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('main.index'))

    form = ReviewForm()
    if form.validate_on_submit():
        # Markdown + bleach
        raw_html = markdown(form.text.data)
        safe_text = bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        review = Review(
            book_id=book.id,
            user_id=current_user.id,
            rating=form.rating.data,
            text=safe_text
        )
        try:
            db.session.add(review)
            db.session.commit()
            flash('Рецензия успешно добавлена.', 'success')
            return redirect(url_for('books.view_book', book_id=book.id))
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при добавлении рецензии: {e}")
            flash('Ошибка при сохранении рецензии. Проверьте корректность введённых данных.', 'danger')
    return render_template('review_form.html', form=form, book=book)


# Добавление книги
@books_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    # Проверка прав (только администратор)
    if current_user.role.name != 'Администратор':
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('main.index'))

    form = BookForm()
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name).all()]

    if form.validate_on_submit():
        try:
            safe_description = bleach.clean(form.description.data, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
            book = Book(
                title=form.title.data,
                description=safe_description,
                year=form.year.data,
                publisher=form.publisher.data,
                author=form.author.data,
                pages=form.pages.data
            )
            book.genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
            db.session.add(book)
            db.session.flush()  # Получаем book.id до коммита

            # Работа с обложкой
            cover_file = form.cover.data
            if cover_file:
                file_bytes = cover_file.read()
                md5_hash = hashlib.md5(file_bytes).hexdigest()
                existing_cover = Cover.query.filter_by(md5_hash=md5_hash).first()
                if existing_cover:
                    book.cover = existing_cover
                else:
                    filename = secure_filename(cover_file.filename)
                    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
                    cover_db = Cover(
                        filename='',  # временно пусто
                        mime_type=cover_file.mimetype,
                        md5_hash=md5_hash,
                        book_id=book.id
                    )
                    db.session.add(cover_db)
                    db.session.flush()  # Получаем cover_db.id

                    new_filename = f"cover_{cover_db.id}.{ext}"
                    cover_db.filename = new_filename
                    book.cover = cover_db

                    covers_dir = os.path.join(current_app.root_path, 'static', 'covers')
                    os.makedirs(covers_dir, exist_ok=True)
                    with open(os.path.join(covers_dir, new_filename), 'wb') as f:
                        f.write(file_bytes)
            else:
                flash('Необходимо загрузить файл обложки.', 'danger')
                return render_template('book_form.html', form=form, mode='add', book=None)

            db.session.commit()
            flash('Книга успешно добавлена.', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при добавлении книги: {e}")
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')

    # Передаем book=None для шаблона, чтобы избежать ошибок
    return render_template('book_form.html', form=form, mode='add', book=None)

# Редактирование книги
@books_bp.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    # Проверка прав (только администратор и модератор)
    if current_user.role.name not in ['Администратор', 'Модератор']:
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('main.index'))

    book = Book.query.get_or_404(book_id)

    # Создаем форму и подгружаем список жанров
    form = BookForm(obj=book)
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name).all()]

    # Для мультиселекта: выставляем выбранные жанры (только при GET)
    if request.method == 'GET':
        form.genres.data = [g.id for g in book.genres]

    # Удаляем поле обложки из формы при редактировании, если оно есть
    if hasattr(form, 'cover'):
        del form.cover

    if form.validate_on_submit():
        try:
            safe_description = bleach.clean(form.description.data, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)

            book.title = form.title.data
            book.description = safe_description
            book.year = form.year.data
            book.publisher = form.publisher.data
            book.author = form.author.data
            book.pages = form.pages.data
            book.genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()

            db.session.commit()
            flash('Книга успешно обновлена.', 'success')
            return redirect(url_for('books.view_book', book_id=book.id))
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при редактировании книги: {e}")
            flash('Ошибка при сохранении изменений. Проверьте корректность введённых данных.', 'danger')

    return render_template('book_form.html', form=form, mode='edit', book=book)

