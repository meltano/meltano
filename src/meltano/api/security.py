from flask_security import Security, SQLAlchemyUserDatastore

from .models import db, User, Role

users = SQLAlchemyUserDatastore(db, User, Role)

DEV_USER = {"email": "dev@meltano.com", "password": "meltano"}

# normally one would setup the extension accordingly, but it
# seems Security.init_app() overwrites all the configuration
security = Security()


def create_dev_user():
    db.create_all()

    if not users.get_user(DEV_USER["email"]):
        users.create_user(**DEV_USER)

    db.session.commit()
