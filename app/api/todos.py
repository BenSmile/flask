from flask import Blueprint, request
from .. models import Todo
from app import db

from . users import token_required

todo = Blueprint('todo', __name__)

@todo.route('/')
@token_required
def get_all_todos(current_user):
   return 'todo'


@todo.route('/<id>', methods = ['GET'])
@token_required
def get_one_todo(current_user, id):
   return 'todo'

@todo.route('/add', methods = ['POST'])
@token_required
def create_todo(current_user):
   data = request.get_json()
   new = Todo(text = data['text'], complete = False, user_id = current_user.id)
   db.session.add(new)
   db.session.commit()
   return 'todo'

@todo.route('/<id>', methods = ['PUT'])
@token_required
def edit_todo(current_user,id):
   return 'todo'

@todo.route('/<id>', methods = ['PUT'])
@token_required
def delete_todo(current_user, id):
   return 'todo'