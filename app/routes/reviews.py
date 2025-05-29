from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import db, Review  
from app.routes.forms import ReviewForm  

reviews = Blueprint('reviews', __name__)

def admin_or_moderator_required():
    if not (current_user.is_authenticated and (current_user.is_admin() or current_user.is_moderator())):
        abort(403)

@reviews.route('/book/<int:book_id>/review/new', methods=['GET', 'POST'])
@login_required
def create_review(book_id):
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            book_id=book_id,
            user_id=current_user.id,
            rating=form.rating.data,
            text=form.text.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Рецензия добавлена', 'success')
        return redirect(url_for('books.view_book', book_id=book_id))
    from app.models import Book
    book = Book.query.get_or_404(book_id)
    return render_template('create_review.html', form=form, book=book)

@reviews.route('/review/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)
    if not (
        current_user.is_authenticated and (
            current_user.id == review.user_id
            or current_user.is_admin()
            or current_user.is_moderator()
        )
    ):
        abort(403)
    form = ReviewForm(obj=review)
    if form.validate_on_submit():
        review.rating = form.rating.data
        review.text = form.text.data
        db.session.commit()
        flash('Рецензия обновлена', 'success')
        return redirect(url_for('books.view_book', book_id=review.book_id))
    return render_template('edit_review.html', form=form, review=review)


@reviews.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    admin_or_moderator_required()
    db.session.delete(review)
    db.session.commit()
    flash('Рецензия удалена', 'success')
    return redirect(url_for('books.view_book', book_id=review.book_id))
