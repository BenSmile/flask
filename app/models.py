from app import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from datetime import datetime

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)


class User(db.Model, UserMixin):
    __tablename__= 'users'
    id = db.Column(db.Integer, primary_key = True)
    public_key = db.Column(db.String(50), unique = True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(64), unique = True, index = True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)
    todos =  db.relationship('Todo', backref='author', lazy=True)
# =================== for test
    username = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    pwd = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime(), default = datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default = datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy = 'dynamic')
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy = 'joined'), lazy = 'dynamic', cascade = 'all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref=db.backref('followed', lazy = 'joined'), lazy = 'dynamic', cascade = 'all, delete-orphan')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name = 'Admin').first()
            else:
                self.role = Role.query.filter_by(name ='User').first()

    def can(self, perm):
        return self.role is None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    @property
    def pwd(self):
        raise AttributeError('password is not a readable attribute')
    
    @pwd.setter
    def pwd(self, pwd):
        self.password_hash = generate_password_hash(pwd)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen= datetime.utcnow
        db.session.add(self)
        db.session.commit()


# ======================================
    def generate_token(self, expires_sec=1800):
        s = Serializer('this must be a SECRET_KEY config', expires_sec)
        return s.dumps({'public_key': self.public_key}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer('this must be a SECRET_KEY config')
        try:
            public_key = s.loads(token)['public_key']
        except:
            return None
        return User.query.get(public_key)

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref = 'role')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def has_permission(self,perm):
        return self.permissions & perm == perm
    
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self, perm):
        self.permissions -= perm
    
    def reset_persmission(self):
        self.permissions=0
    
    @staticmethod
    def insert_roles():
        roles = {
            'User':[Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator':[Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Admin':[Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name = r).first()
            if role is None:
                role = Role(name = r)
            role.reset_persmission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default=(role.name == default_role)
            db.session.add(role)
        db.session.commit()

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow, index = True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False
    
    def is_administrator(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.anonymous_user = AnonymousUser
