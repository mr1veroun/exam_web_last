from datetime import datetime
from app import db  # Импортируй db из app/__init__.py
from flask_login import UserMixin

# Соединительная таблица для связи многие-ко-многим между книгами и жанрами
book_genre = db.Table(
    'book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id', ondelete='CASCADE'), primary_key=True)
)

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)

    def __repr__(self):
        return f"<Genre {self.name}>"

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    genres = db.relationship('Genre', secondary=book_genre, backref='books')
    cover = db.relationship('Cover', uselist=False, backref='book', cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='book', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Book {self.title}>"

class Cover(db.Model):
    __tablename__ = 'cover'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(64), nullable=False)
    md5_hash = db.Column(db.String(32), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"<Cover {self.filename}>"

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f"<Role {self.name}>"

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    middle_name = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    reviews = db.relationship('Review', backref='user', lazy=True, cascade="all, delete-orphan")

    def is_admin(self):
        return self.role and self.role.name == 'Администратор'

    def is_moderator(self):
        return self.role and self.role.name == 'Модератор'

    def __repr__(self):
        return f"<User {self.username}>"


class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Review book={self.book_id} user={self.user_id} rating={self.rating}>"


# Связующая таблица между подборками и книгами
collection_book = db.Table(
    'collection_book',
    db.Column('collection_id', db.Integer, db.ForeignKey('collection.id', ondelete='CASCADE'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), primary_key=True)
)

class Collection(db.Model):
    __tablename__ = 'collection'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref='collections')
    books = db.relationship('Book', secondary=collection_book, backref='collections')

    def __repr__(self):
        return f"<Collection {self.name} user={self.user_id}>"

class BookView(db.Model):
    __tablename__ = 'book_view'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # null для неаутентифицированных
    session_id = db.Column(db.String(128), nullable=True)  # для гостей
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    book = db.relationship('Book')
    user = db.relationship('User')