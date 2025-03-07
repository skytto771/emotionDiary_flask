from app import db

class DiaryEmotionTagLink(db.Model):
    __tablename__ = 'diaryEmotionTagLink'

    linkID = db.Column(db.String(12), primary_key=True, comment='关联的唯一标识')
    diaryID = db.Column(db.String(12), db.ForeignKey('diary.diaryID'), nullable=False, comment='关联的日记ID')
    tagID = db.Column(db.String(12), nullable=False, comment='标签ID')
    result = db.Column(db.String(255), nullable=False, comment='分析原因')
