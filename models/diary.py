from app import db

class Diary(db.Model):
    __tablename__ = 'diary'

    diaryID = db.Column(db.String(12), primary_key=True, comment='日记的唯一标识')
    userID = db.Column(db.String(12), db.ForeignKey('user.userID'), nullable=False, comment='关联的用户ID')
    title = db.Column(db.String(100), nullable=False, comment='日记的标题')
    content = db.Column(db.Text, nullable=False, comment='日记的内容')
    createdDate = db.Column(db.DateTime, nullable=False, comment='日记创建的日期')
