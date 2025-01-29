from app import db

class Reminder(db.Model):
    __tablename__ = 'reminder'

    reminderID = db.Column(db.String(12), primary_key=True, comment='提醒的唯一标识')
    userID = db.Column(db.String(12), db.ForeignKey('user.userID'), nullable=False, comment='关联的用户ID')
    reminderContent = db.Column(db.Text, nullable=False, comment='提醒的具体内容')
    reminderDate = db.Column(db.Date, nullable=False, comment='提醒的日期')
