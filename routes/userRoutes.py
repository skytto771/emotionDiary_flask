from flask import Blueprint, request, jsonify
from models.user import User
from models.utils import generate_unique_user_id, generate_token
from app import db, mail, app
import bcrypt
from datetime import datetime
from flask_mail import Message

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if(user):
        return jsonify({'code': 'PARAM_ERROR','message': '该邮箱已被注册！'}), 403

    username = data['username']
    email = data['email']
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    # 生成唯一的userID
    user_id = generate_unique_user_id()

    new_user = User(
        userID=user_id,
        username=username,
        email=email,
        passwordHash=hashed_password.decode('utf-8'),
        registrationDate=datetime.utcnow()
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'code': 'SUCCESS','message': '用户注册成功!'}), 201
    except Exception as e:
        db.session.rollback()
        print(f'发生了错误{str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        user = User.query.filter_by(email=data['email']).first()
        if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.passwordHash.encode('utf-8')):

            token = generate_token(user.userID)
            user.lastLoginDate = datetime.utcnow()

            db.session.commit()

            return jsonify({'message': '登陆成功!', 'token': token})

        return jsonify({'message': '账号或密码错误'}), 401
    except Exception as e:
        db.session.rollback()
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500

@user_bp.route('/forgotPassword', methods=['POST'])
def forgot_password():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    print([user.email])
    if user:
        # 实现发送重置密码邮件的逻辑
        reset_link = 'https://www.baidu.com'
        # 创建邮件消息
        msg = Message(subject='Password Reset',
                      sender=app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[user.email],
                      body=f"请点击以下链接重置您的密码: {reset_link}")
        # 发送邮件
        mail.send(msg)
        return jsonify({'message': '请前往邮箱重置密码.'}), 200
    return jsonify({'message': '不存在该用户'}), 404
