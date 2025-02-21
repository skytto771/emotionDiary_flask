from flask import Blueprint, request, jsonify
from models.user import User
from models.utils import generate_unique_user_id, generate_token, token_required
from app import db, mail, app
import bcrypt
from datetime import datetime
from flask_mail import Message
import re

user_bp = Blueprint('user', __name__)

def validate_password(password):
    if len(password) < 8:
        return False
    has_lower = any(char.islower() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(not char.isalnum() for char in password)
    return (has_lower and has_upper) or (has_lower and has_digit) or (has_upper and has_digit) or (has_digit and has_special)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # 验证邮箱格式
    email_pattern = re.compile(r'[^@]+@[^@]+\.[^@]+')
    if not email_pattern.match(data.get('email')):
        return jsonify({'code': 'PARAM_ERROR', 'message': '邮箱格式不正确！'}), 403

    user = User.query.filter_by(email=data['email']).first()
    if(user):
        return jsonify({'code': 'PARAM_ERROR','message': '该邮箱已被注册！'}), 403

    password = data.get('password')
    if not validate_password(password):
        return jsonify({'code': 'PARAM_ERROR', 'message': '密码至少包含两种字符类型且不小于8位数！'}), 403

    username = data['username']
    email = data['email']
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # 生成唯一的userID
    user_id = generate_unique_user_id()

    new_user = User(
        userID=user_id,
        username=username,
        email=email,
        passwordHash=hashed_password.decode('utf-8'),
        registrationDate=datetime.now()
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
            user.lastLoginDate = datetime.now()

            db.session.commit()

            return jsonify({'code': 'SUCCESS', 'message': '登陆成功!', 'token': token}), 201

        return jsonify({'code': 'PARAM_ERROR', 'message': '账号或密码错误'}), 401
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


@user_bp.route('/checkLogin', methods=['GET'])
@token_required
def check_login(currentUserId):
    try:
        if currentUserId:
            user = User.query.filter_by(userID=currentUserId).first()
            # 可根据需要返回更多用户信息
            return jsonify({'code': 'SUCCESS', 'message': '用户已登录', 'data': {
                'userID': currentUserId,
                'username': user.username,
            }}), 200

        return jsonify({'code': 'NOT_LOGIN', 'message': '无效的token'}), 401
    except Exception as e:
        print(f'检查登录状态时发生错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500


@user_bp.route('/getUserInfo', methods=['GET'])
@token_required
def getUserInfo(currentUserId):
    try:
        user = User.query.filter_by(userID=currentUserId).first()
        # 可根据需要返回更多用户信息
        return jsonify({'code': 'SUCCESS', 'data': {
            'userID': currentUserId,
            'username': user.username,
            'email': user.email,
        }}), 200

    except Exception as e:
        print(f'发生错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500