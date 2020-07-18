from app.model.user import Users
from app import response, app
from flask import request
from app import db
from flask_jwt_extended import *
from app import mail
from flask_mail import Message
from flask import render_template
import datetime

def index():
    try:
        users = Users.query.all()
        data = transform(users)
        return response.ok(data, "")
    except Exception as e:
        print(e)

def show(id):
    try:
        users = Users.query.filter_by(id=id).first()
        if not users:
            return response.badRequest([], 'Empty....')
        
        data = singleTransform(users)
        return response.ok(data, "")
    except Exception as e:
        print(e)

def store():
    try:
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        users = Users(name=name, email=email)
        users.setPassword(password)
        db.session.add(users)
        db.session.commit()

        msg = Message("Hello {} welcome to Flask".format(name), 
                        sender="nasution.nam@gmail.com")
        msg.add_recipient(email)
        msg.html = render_template('mail.html', app_name="Learn Flask", app_contact="nasution.nam@gmail.com",
                    name=name, email=email)
        
        mail.send(msg)

        return response.ok('', 'Successfully create data!')
    except Exception as e:
        print(e)

def update(id):
    try:
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        user = Users.query.filter_by(id=id).first()
        user.email = email
        user.name = name
        user.setPassword(password)

        db.session.commit()
        return response.ok('', 'Successfully update data!')
    except Exception as e:
        print(e)        

def delete(id):
    try:
        user = Users.query.filter_by(id=id).first()
        if not user:
            return response.badRequest([], 'Empty...')
        
        db.session.delete(user)
        db.session.commit()
        return response.ok('', 'Successfully delete data!')
    except Exception as e:
        print(e)

def login():
    try:
        email = request.json['email']
        password = request.json['password']

        user = Users.query.filter_by(email=email).first()
        if not user:
            return response.badRequest([], 'Empty...')
        
        if not user.checkPassword(password):
            return response.badRequest([], 'Your credentials is invalid')
        
        data = singleTransform(user, withTodo=False)
        expires = datetime.timedelta(days=1)
        expires_refresh = datetime.timedelta(days=3)
        access_token = create_access_token(data, fresh=True, expires_delta=expires)
        refresh_token = create_refresh_token(data, expires_delta=expires_refresh)

        return response.ok({
            "data": data,
            "token_access": access_token,
            "token_refresh": refresh_token
        }, "")
    except Exception as e:
        print(e)

def singleTransform(users, withTodo=True):
    data = {
        'id': users.id,
        'name': users.name,
        'email': users.email,
    }

    if withTodo:
        todos = []
        for i in users.todos:
            todos.append({
                'id': i.id,
                'todo': i.todo,
                'description': i.description,
            })
        data['todos'] = todos

    return data

def transform(users):
    array = []
    for i in users:
        array.append(singleTransform(i))
    return array