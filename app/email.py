from app import mail
from flask_mail import Message
from flask import Blueprint

email = Blueprint('email', __name__)

@email.route('/')
def send():
    msg = Message('Hey smile', recipients=['bawog41991@mailernam.com','kafirongosmile@gmail.com'])
    mail.send(msg)
    return 'Hello World!'


