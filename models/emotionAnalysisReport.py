from app import db

class EmotionAnalysisReport(db.Model):
    __tablename__ = 'emotionAnalysisReport'

    reportID = db.Column(db.String(12), primary_key=True, comment='报告的唯一标识')
    userID = db.Column(db.String(12), db.ForeignKey('user.userID'), nullable=False, comment='关联的用户ID')
    analysisDate = db.Column(db.DateTime, nullable=False, comment='情绪分析的日期')
    emotionCode = db.Column(db.String(50), comment='用于情绪分类的编码')
    emotionFrequency = db.Column(db.Integer, comment='情绪出现的次数')
    emotionTrend = db.Column(db.Text, comment='描述情绪波动的趋势')
    triggerKeywords = db.Column(db.Text, comment='触发情绪的关键词')
