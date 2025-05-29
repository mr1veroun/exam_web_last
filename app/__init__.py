from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from markdown import markdown
import bleach
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

# Разрешённые теги и атрибуты для bleach
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

def markdown_filter(text):
    raw_html = markdown(text or "")
    safe_html = bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    return safe_html

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Регистрируем фильтр markdown для Jinja2
    app.jinja_env.filters['markdown'] = markdown_filter

    # Импортируем и регистрируем Blueprints
    from app.routes.app import main_bp
    from app.routes.books import books_bp
    from app.routes.auth import auth_bp
    from app.routes.reviews import reviews
    from app.routes.collections import collections_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(reviews)
    app.register_blueprint(collections_bp)
    app.register_blueprint(admin_bp)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # login_manager.login_view = 'auth.login'
    # login_manager.login_message_category = 'warning'

    return app
