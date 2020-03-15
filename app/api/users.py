from flask import Blueprint, jsonify, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from .. models import User
from app import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from functools import wraps

user = Blueprint('user', __name__)
s = Serializer('this must be a SECRET_KEY config')


def token_required(f):
    @wraps(f)
    def decorator(*args, ** kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message':'Token is missing'})
        try:
            public_key = s.loads(token)['public_key']
            current_user = User.query.filter_by(public_key=public_key).first()
        except:
            return jsonify({'message': 'Invalid token'})
        return f(current_user, *args, ** kwargs)
    return decorator

@user.route('/', methods=['GET'])
# @token_required
def get_all_users():
    # if not current_user.admin:
    #     return jsonify({'message':'Only admin can perform this'})

    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['public_key'] = user.public_key
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)
    return jsonify({'users ' : output}) 

@user.route('/<public_key>', methods=['GET'])
@token_required
def get_user(current_user, public_key):
    if not current_user.admin:
        return jsonify({'message':'Only admin can perform this'})
    user = User.query.filter_by(public_key=public_key).first()
    if user:
        user_data = {}
        user_data['public_key'] = user.public_key
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        return jsonify({'user':user_data})
    else:
        return jsonify({'message':'No user found for this id'})

@user.route('/add', methods=['POST'])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message':'Only admin can perform this'})
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user = User(public_key = str(uuid.uuid4()), name = data['name'], password = hashed_password, admin = False)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message':'New user has been created'})

@user.route('/<public_key>', methods=['PUT'])
@token_required
def promote_user(current_user, public_key):
    if not current_user.admin:
        return jsonify({'message':'Only admin can perform this'})
    user = User.query.filter_by(public_key = public_key).first()
    if not user:
        return jsonify({'message':'User not found'})
    user.admin = True
    db.session.commit()
    return jsonify({'message':'User has been promoted'})

@user.route('/<public_key>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_key):
    if not current_user.admin:
        return jsonify({'message':'Only admin can perform this'})
    user = User.query.filter_by(public_key = public_key).first()
    if not user:
        return jsonify({'message':'User not found'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message':'User has been deleted'})

@user.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Basic realm="Login required!"'})

    user = User.query.filter_by(name = auth.username).first()

    if check_password_hash(user.password, auth.password):
        token = user.generate_token()
        return jsonify({'token':token})
    
    return make_response('Could not verify', 401, {'WWW-Authenticate':'Basic realm="Login required!"'})
    
    