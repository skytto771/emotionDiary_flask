from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from sqlalchemy import desc

from models.schedule import Schedule
from app import db
from models.utils import token_required, generate_unique_schedule_id, normalize_datetime

schedule_bp = Blueprint('schedule', __name__)

def schedule_to_dict(schedule):
    return {
        'scheduleID': schedule.scheduleID,
        'title': schedule.title,
        'description': schedule.description,
        'is_all_day': schedule.is_all_day,
        'status': schedule.status,
        'reminder_time': schedule.reminder_time,
        'repeat_rule': schedule.repeat_rule,
        'created_at': schedule.created_at,
        'start_time': schedule.start_time,
        'end_time': schedule.end_time
    }

# 检查日程的状态
@schedule_bp.route('/checkScheduleStatus', methods=['GET'])
def check_schedule_status():
    current_time = datetime.now()

    # 获取已经到期且状态为进行中的日程
    expired_schedules = Schedule.query.filter(Schedule.end_time <= current_time, Schedule.status == 1).all()
    for schedule in expired_schedules:
        schedule.status = 2  # 状态标记为已结束

    # 获取正在进行且状态为未开始的日程
    inProgress_schedules = Schedule.query.filter(Schedule.start_time <= current_time, Schedule.end_time >= current_time, Schedule.status == 0).all()
    for schedule in inProgress_schedules:
        schedule.status = 1  # 状态标记为进行中

    # 提交所有更改
    db.session.commit()

    result = '成功执行日程检查程序'
    return jsonify({'code': 'SUCCESS', 'message': result}), 200


@schedule_bp.route('/getScheduleList', methods=['POST'])
@token_required
def get_schedule_list(currentUserId):
    data = request.get_json()
    # 获取请求参数
    title = data.get('title')
    pageCur = data.get('pageCur', 1)  # 默认当前页为1
    pageSize = data.get('pageSize', 30)  # 默认每页30条数据
    status = data.get('status')
    startTime = data.get('start_time')  # 获取开始时间
    endTime = data.get('end_time')      # 获取结束时间

    # 计算偏移量
    offset = (pageCur - 1) * pageSize


    # 查询日记逻辑，筛选出指定用户的日记
    query = Schedule.query.filter(Schedule.userID == currentUserId)

    # 根据标题过滤
    if title:
        query = query.filter(Schedule.title.like(f'%{title}%'))

    # 根据时间范围过滤
    if startTime:
        query = query.filter(Schedule.start_time >= startTime)  # 开始时间
    if endTime:
        query = query.filter(Schedule.start_time <= endTime)    # 结束时间

    if status or status == 0:
        query = query.filter(Schedule.status == status)


    # 执行查询并获取结果，添加分页
    schedules = query.order_by(desc(Schedule.created_at)).limit(pageSize).offset(offset).all()
    schedule_list = []
    for schedule in schedules:
        # 将转换后的日记添加到列表中
        diary_dict = schedule_to_dict(schedule)
        diary_dict['created_at'] = normalize_datetime(schedule.created_at)
        diary_dict['start_time'] = normalize_datetime(schedule.start_time)
        diary_dict['end_time'] = normalize_datetime(schedule.end_time)
        if diary_dict['reminder_time']:
            diary_dict['reminder_time'] = normalize_datetime(schedule.reminder_time)

        schedule_list.append(diary_dict)

    # 获取总记录数
    total_count = query.count()

    return jsonify({'code': 'SUCCESS', 'total': total_count, 'data': schedule_list}), 200

@schedule_bp.route('/addSchedule', methods=['POST'])
@token_required
def add_schedule(currentUserId):
    # 获取请求中的 JSON 数据
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    is_all_day = data.get('is_all_day')
    reminder_time = data.get('reminder_time')
    repeat_rule = data.get('repeat_rule', 0)

    if is_all_day:
        is_all_day = 1
    else:
        is_all_day = 0

    print(is_all_day)

    # 参数校验
    if not title or not start_time or not end_time or not description:
        return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 403

    try:
        # 将字符串时间转换为 datetime 对象
        start_time = normalize_datetime(start_time)
        end_time = normalize_datetime(end_time)
        reminder_time = normalize_datetime(reminder_time) if reminder_time else None

        # 检查日程时间是否合理
        if start_time >= end_time:
            return jsonify({'code': 'PARAM_ERROR', 'message': '开始时间不能晚于或等于结束时间'}), 403

        schedule_id = generate_unique_schedule_id()  # 生成唯一 ID
        new_schedule = Schedule(
            scheduleID=schedule_id,
            userID=currentUserId,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            is_all_day=is_all_day,
            status=0,
            reminder_time=reminder_time,
            repeat_rule=repeat_rule
        )

        db.session.add(new_schedule)
        db.session.commit()
        return jsonify({'code': 'SUCCESS', 'message': '添加成功', 'data': {'scheduleID': schedule_id}}), 201
    except Exception as e:
        db.session.rollback()
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500

@schedule_bp.route('/editSchedule', methods=['post'])
@token_required
def edit_schedule(currentUserId):
    # 获取请求中的 JSON 数据
    data = request.get_json()
    scheduleID = data.get('scheduleID')
    title = data.get('title')
    description = data.get('description')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    is_all_day = data.get('is_all_day', 0)
    reminder_time = data.get('reminder_time')
    repeat_rule = data.get('repeat_rule', 0)
    status = data.get('status', 0)  # 允许更新状态


    # 参数校验
    if not title or not start_time or not end_time or not description:
        return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 403

    try:
        # 将字符串时间转换为 datetime 对象
        start_time = normalize_datetime(start_time)
        end_time = normalize_datetime(end_time)
        reminder_time = normalize_datetime(reminder_time) if reminder_time else None

        # 检查日程时间是否合理
        if start_time >= end_time:
            return jsonify({'code': 'PARAM_ERROR', 'message': '开始时间不能晚于或等于结束时间'}), 403

        # 查找并更新指定日程
        schedule = Schedule.query.filter_by(scheduleID=scheduleID, userID=currentUserId).first()
        if not schedule:
            return jsonify({'code': 'NOT_FOUND', 'message': '日程不存在'}), 404

        # 更新日程信息
        schedule.title = title
        schedule.description = description
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.is_all_day = is_all_day
        schedule.status = status
        schedule.reminder_time = reminder_time
        schedule.repeat_rule = repeat_rule

        # 提交更改
        db.session.commit()
        return jsonify({'code': 'SUCCESS', 'message': '编辑成功', 'data': {'scheduleID': scheduleID}}), 200

    except Exception as e:
        db.session.rollback()
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500


@schedule_bp.route('/deleteSchedule', methods=['post'])
@token_required
def delete_schedule(currentUserId):
    # 获取请求中的 JSON 数据
    data = request.get_json()
    scheduleID = data.get('scheduleID')  # 提取要删除的日程 ID

    # 参数校验
    if not scheduleID:
        return jsonify({'code': 'PARAM_ERROR', 'message': '缺少日程 ID'}), 403

    try:
        # 查找指定的日程
        schedule = Schedule.query.filter_by(scheduleID=scheduleID, userID=currentUserId).first()
        if not schedule:
            return jsonify({'code': 'NOT_FOUND', 'message': '日程不存在'}), 404

            # 删除日程
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({'code': 'SUCCESS', 'message': '日程删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500