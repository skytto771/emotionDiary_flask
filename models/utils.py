import uuid
from flask import jsonify, request
from app import db,app
from models.fileSlice import FileSlice
from models.user import User
from models.diary import Diary
from models.userAvatar import UserAvatar
from models.diaryEmotionTagLink import DiaryEmotionTagLink
from models.files import File
import jwt
from datetime import datetime, timedelta
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

def generate_unique_file_id(length=12):
    while True:
        # 生成一个UUID，并去掉连字符
        uuid_str = uuid.uuid4().hex
        # 截取指定长度的字符
        file_id = uuid_str[:length]
        # 检查数据库中是否存在该userID
        existing_file = File.query.filter_by(fileID=file_id).first()
        if not existing_file:
            # 如果不存在，则返回该userID
            return file_id
        # 如果存在，则继续循环生成新的ID

def generate_unique_fileSlice_id(length=12):
    while True:
        # 生成一个UUID，并去掉连字符
        uuid_str = uuid.uuid4().hex
        # 截取指定长度的字符
        slice_id = uuid_str[:length]
        # 检查数据库中是否存在该userID
        existing_file = FileSlice.query.filter_by(sliceID=slice_id).first()
        if not existing_file:
            # 如果不存在，则返回该userID
            return slice_id
        # 如果存在，则继续循环生成新的ID

def generate_unique_avatar_id(length=12):
    while True:
        # 生成一个UUID，并去掉连字符
        uuid_str = uuid.uuid4().hex
        # 截取指定长度的字符
        avatar_id = uuid_str[:length]
        # 检查数据库中是否存在该userID
        existing_file = UserAvatar.query.filter_by(avatarID=avatar_id).first()
        if not existing_file:
            # 如果不存在，则返回该userID
            return avatar_id
        # 如果存在，则继续循环生成新的ID

def generate_unique_schedule_id(length=12):
    while True:
        # 生成一个UUID，并去掉连字符
        uuid_str = uuid.uuid4().hex
        # 截取指定长度的字符
        avatar_id = uuid_str[:length]
        # 检查数据库中是否存在该userID
        existing_file = UserAvatar.query.filter_by(avatarID=avatar_id).first()
        if not existing_file:
            # 如果不存在，则返回该userID
            return avatar_id
        # 如果存在，则继续循环生成新的ID


def generate_token(user_id):
    token = jwt.encode({
        'userID': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)  # Token有效期1小时
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

from datetime import datetime

def normalize_datetime(input_datetime):
    """
    将多种时间格式统一转换为 %Y-%m-%d %H:%M:%S 格式的字符串。

    支持的时间格式：
    - 时间戳（整数或浮点数）
    - ISO 格式字符串（如 2023-10-15T09:00:00）
    - 常见日期时间字符串（如 2023-10-15 09:00:00 或 2023/10/15 09:00:00）
    - 仅日期字符串（如 2023-10-15）

    参数:
    input_datetime: 输入的时间，可以是时间戳、字符串或 datetime 对象。

    返回:
    格式化后的时间字符串（%Y-%m-%d %H:%M:%S）。

    异常:
    如果无法解析输入的时间格式，抛出 ValueError。
    """
    if isinstance(input_datetime, (int, float)):  # 处理时间戳
        dt = datetime.fromtimestamp(input_datetime)
    elif isinstance(input_datetime, str):  # 处理字符串
        # 尝试多种日期时间格式
        formats = [
            '%Y-%m-%d %H:%M:%S',  # 2023-10-15 09:00:00
            '%Y/%m/%d %H:%M:%S',  # 2023/10/15 09:00:00
            '%Y-%m-%dT%H:%M:%S',  # ISO 格式 2023-10-15T09:00:00
            '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO 格式带毫秒和时区 2025-03-03T16:00:00.000Z
            '%Y-%m-%d %H:%M',  # 2023-10-15 09:00
            '%Y/%m/%d %H:%M',  # 2023/10/15 09:00
            '%Y-%m-%d',  # 2023-10-15
            '%Y/%m/%d',  # 2023/10/15
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(input_datetime, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"无法解析日期字符串: {input_datetime}")
    elif isinstance(input_datetime, datetime):  # 处理 datetime 对象
        dt = input_datetime
    else:
        raise ValueError("不支持的时间格式")
    # 返回统一格式的字符串
    return dt.strftime('%Y-%m-%d %H:%M:%S')