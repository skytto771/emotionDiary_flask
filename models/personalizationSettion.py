from app import db

class PersonalizationSetting(db.Model):
    __tablename__ = 'personalizationSetting'

    settingID = db.Column(db.String(12), primary_key=True, comment='设置的唯一标识')
    userID = db.Column(db.String(12), db.ForeignKey('user.userID'), nullable=False, comment='关联的用户ID')
    themeStyle = db.Column(db.String(50), comment='用户选择的主题风格')
    fontStyle = db.Column(db.String(50), comment='用户选择的字体风格')
    reportFrequency = db.Column(db.Integer, comment='报告生成的频率')
