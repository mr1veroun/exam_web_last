from app import create_app, db
from app.models import Role, User
from werkzeug.security import generate_password_hash

# === НАСТРОЙ ДАННЫЕ АДМИНА ЗДЕСЬ ===
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Обязательно придумай сложный пароль!
ADMIN_LAST_NAME = "Иванов"
ADMIN_FIRST_NAME = "Админ"
ADMIN_MIDDLE_NAME = "Админович"

app = create_app()
with app.app_context():
    # 1. Создаем роль "Администратор", если ее нет
    admin_role = Role.query.filter_by(name='Администратор').first()
    if not admin_role:
        admin_role = Role(name='Администратор', description='Суперпользователь')
        db.session.add(admin_role)
        db.session.commit()
        print("Роль 'Администратор' создана.")

    # 2. Проверяем, есть ли уже такой пользователь
    admin_user = User.query.filter_by(username=ADMIN_USERNAME).first()
    if not admin_user:
        admin_user = User(
            username=ADMIN_USERNAME,
            password_hash=generate_password_hash(ADMIN_PASSWORD),
            last_name=ADMIN_LAST_NAME,
            first_name=ADMIN_FIRST_NAME,
            middle_name=ADMIN_MIDDLE_NAME,
            role_id=admin_role.id
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"Пользователь-администратор '{ADMIN_USERNAME}' успешно создан!")
        print(f"Логин: {ADMIN_USERNAME}")
        print(f"Пароль: {ADMIN_PASSWORD}")
    else:
        print(f"Пользователь с логином '{ADMIN_USERNAME}' уже существует.")
