from app import db

class EmotionTag(db.Model):
    __tablename__ = 'emotionTag'

    tagID = db.Column(db.String(12), primary_key=True, comment='情绪标签的唯一标识')
    tagName = db.Column(db.String(50), nullable=False, unique=True, comment='情绪标签的名称')
