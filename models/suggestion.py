from app import db

class Suggestion(db.Model):
    __tablename__ = 'suggestion'

    suggestionID = db.Column(db.String(12), primary_key=True, comment='建议的唯一标识')
    userID = db.Column(db.String(12), db.ForeignKey('user.userID'), nullable=False, comment='关联的用户ID')
    suggestionContent = db.Column(db.Text, nullable=False, comment='建议的具体内容')
    suggestionType = db.Column(db.String(50), comment='建议的类型')
    suggestionDate = db.Column(db.Date, nullable=False, comment='建议的日期')
