from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Collection, Book

collections_bp = Blueprint('collections', __name__)

@collections_bp.route('/collections')
@login_required
def my_collections():
    if current_user.role.name != 'Пользователь':
        flash('Доступ разрешён только для пользователей.', 'danger')
        return redirect(url_for('main.index'))
    collections = Collection.query.filter_by(user_id=current_user.id).all()
    return render_template('my_collections.html', collections=collections)

@collections_bp.route('/collections/<int:collection_id>')
@login_required
def view_collection(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    if collection.user_id != current_user.id:
        flash('Нет доступа к этой подборке.', 'danger')
        return redirect(url_for('my_collections.html'))
    return render_template('view_collection.html', collection=collection)

@collections_bp.route('/collections/add', methods=['POST'])
@login_required
def add_collection():
    name = request.form.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'message': 'Название не может быть пустым.'}), 400
    new_collection = Collection(name=name, user_id=current_user.id)
    db.session.add(new_collection)
    db.session.commit()
    flash('Подборка успешно создана!', 'success')
    return jsonify({'success': True, 'redirect': url_for('my_collections')})

@collections_bp.route('/collections/<int:collection_id>/add_book', methods=['POST'])
@login_required
def add_book_to_collection(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    if collection.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Нет доступа.'}), 403
    book_id = request.form.get('book_id', type=int)
    if not book_id:
        return jsonify({'success': False, 'message': 'Некорректная книга.'}), 400
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success': False, 'message': 'Книга не найдена.'}), 404
    if book in collection.books:
        return jsonify({'success': False, 'message': 'Книга уже в подборке.'}), 400
    collection.books.append(book)
    db.session.commit()
    flash('Книга добавлена в подборку!', 'success')
    return jsonify({'success': True, 'redirect': url_for('books.view_book', book_id=book.id)})
