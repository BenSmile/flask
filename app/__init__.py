from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from flask_login import LoginManager
from flask_mail import Mail


db = SQLAlchemy()
mail = Mail()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    from app import models
    from app.main.routes import main
    from app.api.todos import todo as api_todo
    from app.api.users import user as api_user
    from app.auth import auth as authentification_blueprint
    from app.email import email as email_blueprint

    app.register_blueprint(main)
    app.register_blueprint(email_blueprint, url_prefix = '/email')
    app.register_blueprint(authentification_blueprint, url_prefix = '/auth')
    app.register_blueprint(api_todo, url_prefix = '/todo')
    app.register_blueprint(api_user, url_prefix = '/user')

    return app