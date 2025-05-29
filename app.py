from flask import Blueprint, render_template, request, session
from flask_login import current_user
from app.models import db, Book, Review, Genre, BookView
from sqlalchemy import func
from datetime import datetime, date, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    # --- Фильтры поиска ---
    title = request.args.get('title', '').strip()
    author = request.args.get('author', '').strip()
    genres_selected = request.args.getlist('genre')
    years_selected = request.args.getlist('year')
    pages_from = request.args.get('pages_from', type=int)
    pages_to = request.args.get('pages_to', type=int)
    page = request.args.get('page', 1, type=int)

    query = Book.query

    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if genres_selected:
        query = query.join(Book.genres).filter(Genre.id.in_([int(g) for g in genres_selected]))
    if years_selected:
        query = query.filter(Book.year.in_([int(y) for y in years_selected if y.isdigit()]))
    if pages_from:
        query = query.filter(Book.pages >= pages_from)
    if pages_to:
        query = query.filter(Book.pages <= pages_to)

    genres = Genre.query.order_by(Genre.name).all()
    years = sorted({b.year for b in Book.query.with_entities(Book.year).distinct()})

    pagination = query.order_by(Book.year.desc()).paginate(page=page, per_page=9, error_out=False)
    books = pagination.items

    books_data = []
    for book in books:
        avg_rating = db.session.query(func.avg(Review.rating)).filter(Review.book_id == book.id).scalar()
        review_count = db.session.query(func.count(Review.id)).filter(Review.book_id == book.id).scalar()
        books_data.append({
            'book': book,
            'genres': book.genres,
            'avg_rating': round(avg_rating, 2) if avg_rating else '—',
            'review_count': review_count
        })

    # --- Популярные книги за последние 3 месяца ---
    now = datetime.utcnow()
    three_months_ago = now - timedelta(days=90)
    popular_books = db.session.query(
        Book, func.count(BookView.id).label('views')
    ).join(BookView).filter(
        BookView.viewed_at >= three_months_ago
    ).group_by(Book.id).order_by(func.count(BookView.id).desc()).limit(5).all()
    # popular_books: список кортежей (Book, views)

    # --- Недавно просмотренные книги ---
    recent_books = []
    if current_user.is_authenticated:
        recent_views = BookView.query.filter_by(user_id=current_user.id).order_by(BookView.viewed_at.desc()).limit(5).all()
        recent_books = [v.book for v in recent_views]
    else:
        session_id = session.get('sid')
        if session_id:
            recent_views = BookView.query.filter_by(session_id=session_id).order_by(BookView.viewed_at.desc()).limit(5).all()
            recent_books = [v.book for v in recent_views]
    user_reviews = {}

    if current_user.is_authenticated:
        book_ids = [item['book'].id for item in books_data]
        if book_ids:
            reviews = Review.query.filter(
                Review.user_id == current_user.id,
                Review.book_id.in_(book_ids)
            ).all()
            user_reviews = {review.book_id: review for review in reviews}

    return render_template(
        "index.html",
        books_data=books_data,
        genres=genres,
        years=years,
        pagination=pagination,
        popular_books=popular_books,
        recent_books=recent_books, 
        user_reviews=user_reviews 
    )
