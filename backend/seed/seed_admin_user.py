from app import app
from database import db
from models_auth import LibrarianUser


def seed_default_admin(username='admin', password='Admin@123', full_name='Administrateur principal'):
    with app.app_context():
        db.create_all()

        user = LibrarianUser.query.filter_by(username=username).first()
        if user:
            user.role = 'admin'
            user.is_active = True
            db.session.commit()
            print(f"Utilisateur déjà existant, rôle admin confirmé : {username}")
            print("Mot de passe inchangé. Si besoin, supprime l'utilisateur puis relance le script.")
            return

        user = LibrarianUser(username=username, full_name=full_name, role='admin', is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        print('Utilisateur administrateur créé avec succès.')
        print(f'username: {username}')
        print(f'password: {password}')


if __name__ == '__main__':
    seed_default_admin()
