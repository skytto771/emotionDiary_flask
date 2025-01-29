from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from models.diary import Diary
from app import db
from models.utils import token_required, generate_unique_diary_id

diary_bp = Blueprint('diary', __name__)


def diary_to_dict(diary):
    return {
        'diaryID': diary.diaryID,
        'userID': diary.userID,
        'title': diary.title,
        'content': diary.content,
        'createdDate': diary.createdDate.isoformat()  # 将日期时间转换为字符串格式
    }


@diary_bp.route('/getDiaries', methods=['GET'])
@token_required
def get_diary(currentUserId):
    # 查询日记逻辑
    diaries = Diary.query.filter_by(userID=currentUserId).all()
    diary_list = [diary_to_dict(diary) for diary in diaries]
    return jsonify({'code': 'SUCCESS', 'data': diary_list}), 201


@diary_bp.route('/addDiary', methods=['post'])
@token_required
def add_diary(currentUserId):
    # 添加日记逻辑
    data = request.get_json()
    title = data['title']
    content = data['content']

    if not title or not content:
        return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 403

    diary_id = generate_unique_diary_id()

    new_diary = Diary(
        diaryID=diary_id,
        userID=currentUserId,
        title=title,
        content=content,
        createdDate=datetime.utcnow(),
    )

    try:
        db.session.add(new_diary)
        db.session.commit()
        return jsonify({'code': 'SUCCESS', 'message': '添加成功'}), 201
    except Exception as e:
        db.session.rollback()
        print(f'发生了错误{str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500


@diary_bp.route('/updateDiary', methods=['POST'])
@token_required
def update_diary(currentUserId):
    # 获取请求中的 JSON 数据
    data = request.get_json()
    diaryID = data.get('diaryID')
    title = data.get('title')
    content = data.get('content')

    # 参数校验
    if not diaryID or (not title and not content):
        return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 403

    try:
        # 查询日记
        diary = Diary.query.filter_by(diaryID=diaryID, userID=currentUserId).first()

        if not diary:
            return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 404

        # 获取日记的创建日期
        diary_date = diary.createdDate  # 假设 createdDate 为日记创建日期字段
        today = datetime.now().date()

        # 检查是否为昨天的日记
        if diary_date.date() == (today - timedelta(days=1)):
            return jsonify({'code': 'FORBIDDEN', 'message': '不可修改昨天的日记'}), 403

        # 更新标题和内容
        if title:
            diary.title = title
        if content:
            diary.content = content

        # 提交更改到数据库
        db.session.commit()
        return jsonify({'code': 'SUCCESS', 'message': '更新成功'}), 200

    except Exception as e:
        db.session.rollback()
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500


@diary_bp.route('/deleteDiary', methods=['DELETE'])
@token_required
def delete_diary(currentUserId):
    # 获取请求中的 JSON 数据
    data = request.get_json()
    diaryID = data.get('diaryID')

    # 参数校验
    if not diaryID:
        return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 403

    try:
        # 查询日记
        diary = Diary.query.filter_by(diaryID=diaryID, userID=currentUserId).first()

        if not diary:
            return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 404

        # 从数据库中删除该日记
        db.session.delete(diary)
        db.session.commit()

        return jsonify({'code': 'SUCCESS', 'message': '删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500
