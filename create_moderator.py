from app import create_app, db
from app.models import Role, User
from werkzeug.security import generate_password_hash

# === НАСТРОЙ ДАННЫЕ МОДЕРАТОРА ЗДЕСЬ ===
MODERATOR_USERNAME = "moderator"
MODERATOR_PASSWORD = "moderator123"  # Придумай сложный пароль!
MODERATOR_LAST_NAME = "Петров"
MODERATOR_FIRST_NAME = "Модератор"
MODERATOR_MIDDLE_NAME = "Модераторович"

app = create_app()
with app.app_context():
    # 1. Создать роль "Модератор", если ее нет
    moderator_role = Role.query.filter_by(name='Модератор').first()
    if not moderator_role:
        moderator_role = Role(name='Модератор', description='Пользователь с расширенными правами')
        db.session.add(moderator_role)
        db.session.commit()
        print("Роль 'Модератор' создана.")

    # 2. Проверить, есть ли уже такой пользователь
    moderator_user = User.query.filter_by(username=MODERATOR_USERNAME).first()
    if not moderator_user:
        moderator_user = User(
            username=MODERATOR_USERNAME,
            password_hash=generate_password_hash(MODERATOR_PASSWORD),
            last_name=MODERATOR_LAST_NAME,
            first_name=MODERATOR_FIRST_NAME,
            middle_name=MODERATOR_MIDDLE_NAME,
            role_id=moderator_role.id
        )
        db.session.add(moderator_user)
        db.session.commit()
        print(f"Пользователь-модератор '{MODERATOR_USERNAME}' успешно создан!")
        print(f"Логин: {MODERATOR_USERNAME}")
        print(f"Пароль: {MODERATOR_PASSWORD}")
    else:
        print(f"Пользователь с логином '{MODERATOR_USERNAME}' уже существует.")
