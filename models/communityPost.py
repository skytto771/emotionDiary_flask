from app import db

class CommunityPost(db.Model):
    __tablename__ = 'communityPost'

    postID = db.Column(db.String(12), primary_key=True, comment='帖子的唯一标识')
    userID = db.Column(db.String(12), db.ForeignKey('user.userID'), nullable=False, comment='关联的用户ID')
    title = db.Column(db.String(100), nullable=False, comment='帖子的标题')
    content = db.Column(db.Text, nullable=False, comment='帖子的内容')
    createdDate = db.Column(db.DateTime, nullable=False, comment='帖子创建的日期')
