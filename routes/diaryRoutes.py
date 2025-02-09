from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from sqlalchemy import desc

from models.diary import Diary
from models.diaryEmotionTagLink import DiaryEmotionTagLink
from models.emotionTag import EmotionTag
from app import db
from models.utils import token_required, generate_unique_diary_id, generate_unique_linkID

diary_bp = Blueprint('diary', __name__)


def diary_to_dict(diary):
    return {
        'diaryID': diary.diaryID,
        'userID': diary.userID,
        'title': diary.title,
        'content': diary.content,
        'content_html': diary.content_html,
        'createdDate': diary.createdDate.isoformat()  # 将日期时间转换为字符串格式
    }

def diaryLinkToDict(link):
    return {
        'linkID': link.linkID,
        'diaryID': link.linkID,
        'tagID': link.linkID,
    }


@diary_bp.route('/getDiaries', methods=['POST'])
@token_required
def get_diary(currentUserId):
    data = request.get_json()

    # 获取请求参数
    startTime = data.get('startTime')
    endTime = data.get('endTime')
    diaryTitle = data.get('diaryTitle')

    # 处理日期范围
    try:
        if startTime:
            start_datetime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")  # 可以根据需要调整格式
        else:
            start_datetime = None

        if endTime:
            end_datetime = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")  # 可以根据需要调整格式
        else:
            end_datetime = None
    except ValueError:
        return jsonify({'code': 'PARAM_ERROR', 'message': '时间格式错误'}), 400

    # 如果没有提供日期，则默认设定为当前月份的开始和结束时间
    if not start_datetime and not end_datetime:
        today = datetime.now()
        start_datetime = datetime(today.year, today.month, 1)
        end_datetime = (start_datetime + timedelta(days=31)).replace(day=1)  # 下个月的第一天

    # 查询日记逻辑，筛选出在指定时间范围内的日记
    diary = Diary.query.filter(Diary.userID == currentUserId)
    query = diary

    # 根据日期范围过滤
    if start_datetime:
        query = query.filter(Diary.createdDate >= start_datetime)

    if end_datetime:
        query = query.filter(Diary.createdDate < end_datetime)  # 注意这里用小于下个月的第一天

    # 根据标题过滤
    if diaryTitle:
        query = query.filter(Diary.title.like(f'%{diaryTitle}%'))

    # 执行查询并获取结果
    diaries = query.order_by(desc(Diary.createdDate)).all()
    diary_list = []
    for diary in diaries:
        DELink = DiaryEmotionTagLink.query.filter_by(diaryID=diary.diaryID).first()
        tag = EmotionTag.query.filter_by(tagID=DELink.tagID).first()
        # 将转换后的日记添加到列表中
        diary_dict = diary_to_dict(diary)
        diary_dict['tagName'] = tag.tagName
        diary_dict['tagID'] = tag.tagID
        diary_list.append(diary_dict)

    return jsonify({'code': 'SUCCESS', 'data': diary_list}), 201


@diary_bp.route('/getDiaryDetail', methods=['post'])
@token_required
def get_diary_detail(currentUserId):
    data = request.get_json()
    diaryID = data['diaryID']

    # 根据用户 ID 和日记 ID 查询日记
    diary = Diary.query.filter_by(diaryID=diaryID, userID=currentUserId).first()

    if not diary:
        return jsonify({'code': 'NOT_FOUND', 'message': '日记未找到'}), 404

    # 将日记对象转换为字典格式（假设你有 diary_to_dict 函数）
    diary_details = diary_to_dict(diary)

    return jsonify({'code': 'SUCCESS', 'data': diary_details}), 200


@diary_bp.route('/addDiary', methods=['post'])
@token_required
def add_or_update_diary(currentUserId):
    # 获取请求中的 JSON 数据
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    content_html = data.get('content_html')
    diaryID = data.get('diaryID')

    # 参数校验
    if not title or not content:
        return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 403

    curDate = datetime.now().strftime('%Y-%m-%d')
    diary = Diary.query.filter_by(createdDate=curDate, userID=currentUserId, diaryID=diaryID).first()

    try:
        if diary:
            # 如果今天已经存在日记，检查是否能够修改
            diary_date = diary.createdDate  # 假设 createdDate 为日记创建日期字段
            today = datetime.now().date()

            # 检查是否为非今天的日记
            if diary_date.date() != today:
                return jsonify({'code': 'FORBIDDEN', 'message': '不可修改该日记'}), 403

            # 更新标题和内容
            diary.title = title
            diary.content = content.encode('utf-8').decode('utf-8')
            diary.content_html = content_html.encode('utf-8').decode('utf-8')

            db.session.commit()
            return jsonify({'code': 'SUCCESS', 'message': '更新成功', 'data': {'diaryID': diaryID}}), 200
        else:
            # 如果今天没有日记，则添加新的日记
            diary_id = generate_unique_diary_id()
            link_id = generate_unique_linkID()

            new_diary = Diary(
                diaryID=diary_id,
                userID=currentUserId,
                title=title,
                content=content,
                content_html=content_html,
                createdDate=curDate,
            )

            new_link = DiaryEmotionTagLink(
                linkID=link_id,
                diaryID=diary_id,
                tagID=-1,
            )

            db.session.add(new_diary)
            db.session.add(new_link)
            db.session.commit()
            return jsonify({'code': 'SUCCESS', 'message': '添加成功', 'data': {'diaryID':diary_id}}), 201

    except Exception as e:
        db.session.rollback()
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500


# @diary_bp.route('/updateDiary', methods=['POST'])
# @token_required
# def update_diary(currentUserId):
#     # 获取请求中的 JSON 数据
#     data = request.get_json()
#     diaryID = data.get('diaryID')
#     title = data.get('title')
#     content = data.get('content')
#
#     # 参数校验
#     if not diaryID or (not title and not content):
#         return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 403
#
#     try:
#         # 查询日记
#         diary = Diary.query.filter_by(diaryID=diaryID, userID=currentUserId).first()
#
#         if not diary:
#             return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 404
#
#         # 获取日记的创建日期
#         diary_date = diary.createdDate  # 假设 createdDate 为日记创建日期字段
#         today = datetime.now().date()
#
#         # 检查是否为昨天的日记
#         if diary_date.date() == (today - timedelta(days=1)):
#             return jsonify({'code': 'NO_AUTH', 'message': '不可修改昨天的日记'}), 403
#
#         # 更新标题和内容
#         if title:
#             diary.title = title
#         if content:
#             diary.content = content
#
#         # 提交更改到数据库
#         db.session.commit()
#         return jsonify({'code': 'SUCCESS', 'message': '更新成功'}), 200
#
#     except Exception as e:
#         db.session.rollback()
#         print(f'发生了错误: {str(e)}')
#         return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500


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
