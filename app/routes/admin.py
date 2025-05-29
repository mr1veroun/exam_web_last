from flask import Blueprint, abort, render_template, request, send_file
from flask_login import login_required, current_user
from app.models import db, BookView, Book, User
from sqlalchemy import func
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/stats')
@login_required
def stats():
    if not current_user.is_admin():
        abort(403)
    tab = request.args.get('tab', 'log')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Журнал действий пользователей
    if tab == 'log':
        query = BookView.query.order_by(BookView.viewed_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return render_template('stats.html', tab='log', pagination=pagination)

    # Статистика просмотра книг
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    filters = []
    if date_from:
        filters.append(BookView.viewed_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        filters.append(BookView.viewed_at <= datetime.strptime(date_to, '%Y-%m-%d'))
    query = db.session.query(
        Book.title, func.count(BookView.id).label('views')
    ).join(BookView).filter(
        BookView.user_id.isnot(None), *filters
    ).group_by(Book.id).order_by(func.count(BookView.id).desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('stats.html', tab='stats', pagination=pagination, date_from=date_from, date_to=date_to)

import csv
from io import StringIO
from flask import make_response

@admin_bp.route('/admin/stats/export')
@login_required
def export_stats():
    if not current_user.is_admin():
        abort(403)
    tab = request.args.get('tab', 'log')
    si = StringIO()
    cw = csv.writer(si)
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{tab}_export_{now}.csv"

    if tab == 'log':
        cw.writerow(['№', 'Пользователь', 'Книга', 'Дата и время'])
        views = BookView.query.order_by(BookView.viewed_at.desc()).all()
        for i, v in enumerate(views, 1):
            fio = f"{v.user.last_name} {v.user.first_name}" if v.user else "Неаутентифицированный пользователь"
            cw.writerow([i, fio, v.book.title, v.viewed_at])
    else:
        # Статистика по книгам
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        filters = []
        if date_from:
            filters.append(BookView.viewed_at >= datetime.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            filters.append(BookView.viewed_at <= datetime.strptime(date_to, '%Y-%m-%d'))
        query = db.session.query(
            Book.title, func.count(BookView.id).label('views')
        ).join(BookView).filter(
            BookView.user_id.isnot(None), *filters
        ).group_by(Book.id).order_by(func.count(BookView.id).desc())
        cw.writerow(['№', 'Книга', 'Количество просмотров'])
        for i, row in enumerate(query.all(), 1):
            cw.writerow([i, row[0], row[1]])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-type"] = "text/csv"
    return output
