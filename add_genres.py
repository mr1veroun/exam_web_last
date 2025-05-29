from app import db
from app.models import Genre

genres = [
    "Фантастика",
    "Детектив",
    "Роман",
    "Научная литература",
    "Приключения"
]

for name in genres:
    if not Genre.query.filter_by(name=name).first():
        db.session.add(Genre(name=name))
db.session.commit()
print(Genre.query.all())
