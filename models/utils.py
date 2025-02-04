import uuid
from flask import jsonify, request
from app import db,app
from models.user import User
from models.diary import Diary
from models.diaryEmotionTagLink import DiaryEmotionTagLink
import jwt
import datetime
from functools import wraps


def generate_unique_user_id(length=12):
    """
    生成一个唯一的userID，通过截取UUID的一部分。
    如果生成的ID已存在，则重新生成，直到找到一个唯一的ID为止。

    :param length: 生成ID的长度，默认为12
    :return: 一个唯一的userID字符串
    """
    while True:
        # 生成一个UUID，并去掉连字符
        uuid_str = uuid.uuid4().hex
        # 截取指定长度的字符
        user_id = uuid_str[:length]
        # 检查数据库中是否存在该userID
        existing_user = User.query.filter_by(userID=user_id).first()
        if not existing_user:
            # 如果不存在，则返回该userID
            return user_id
        # 如果存在，则继续循环生成新的ID


def generate_unique_linkID(length=12):
    """
    生成一个唯一的userID，通过截取UUID的一部分。
    如果生成的ID已存在，则重新生成，直到找到一个唯一的ID为止。

    :param length: 生成ID的长度，默认为12
    :return: 一个唯一的userID字符串
    """
    while True:
        # 生成一个UUID，并去掉连字符
        uuid_str = uuid.uuid4().hex
        # 截取指定长度的字符
        linkID = uuid_str[:length]
        # 检查数据库中是否存在该userID
        existing_user = DiaryEmotionTagLink.query.filter_by(linkID=linkID).first()
        if not existing_user:
            # 如果不存在，则返回该userID
            return linkID
        # 如果存在，则继续循环生成新的ID


def generate_unique_diary_id(length=12):
    """
    生成一个唯一的userID，通过截取UUID的一部分。
    如果生成的ID已存在，则重新生成，直到找到一个唯一的ID为止。

    :param length: 生成ID的长度，默认为12
    :return: 一个唯一的userID字符串
    """
    while True:
        # 生成一个UUID，并去掉连字符
        uuid_str = uuid.uuid4().hex
        # 截取指定长度的字符
        diary_id = uuid_str[:length]
        # 检查数据库中是否存在该diaryId
        existing_diary = Diary.query.filter_by(diaryID=diary_id).first()
        existing_user = User.query.filter_by(userID=diary_id).first()
        if not existing_user and not existing_diary:
            # 如果不存在，则返回该userID
            return diary_id
        # 如果存在，则继续循环生成新的ID


def generate_token(user_id):
    token = jwt.encode({
        'userID': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token有效期1小时
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return token



def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # 检查请求头中是否存在 token
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return jsonify({'code': 'NOT_LOGIN', 'message': '未提供认证信息'}), 401

        try:
            # 解码 token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            currentUserId = data['userID']

            # 可以根据 userID 查询用户信息
        except Exception as e:
            print(e)
            return jsonify({"code": "NOT_LOGIN", 'message': '无效的 token!'}), 403

        return f(currentUserId, *args, **kwargs)  # 将当前用户ID传递给被装饰的函数
    return decorated_function