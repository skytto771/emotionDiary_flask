from app import db
from datetime import datetime

class Schedule(db.Model):
    __tablename__ = 'schedules'

    scheduleID = db.Column(db.String(12), primary_key=True, comment='唯一标识日程')
    title = db.Column(db.String(255), nullable=False, comment='日程标题')
    description = db.Column(db.Text, comment='日程描述')
    start_time = db.Column(db.DateTime, nullable=False, comment='开始时间')
    end_time = db.Column(db.DateTime, nullable=False, comment='结束时间')
    is_all_day = db.Column(db.Integer, default=0, comment='是否为全天事件')
    status = db.Column(db.Integer, comment='日程状态')
    reminder_time = db.Column(db.DateTime, comment='提醒时间')
    repeat_rule = db.Column(db.Integer, default=0, comment='重复规则')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    userID = db.Column(db.String(12), db.ForeignKey('user.userID'), nullable=False, comment='与用户表的关联ID')

    # 定义与 User 模型的关系
    user = db.relationship('User', backref='schedules')

    def __repr__(self):
        return f"<Schedule {self.scheduleID}: {self.title}>"