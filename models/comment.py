from app import db

class Comment(db.Model):
    __tablename__ = 'comment'

    commentID = db.Column(db.String(12), primary_key=True, comment='评论的唯一标识')
    postID = db.Column(db.String(12), db.ForeignKey('communityPost.postID'), nullable=False, comment='关联的帖子ID')
    userID = db.Column(db.String(12), db.ForeignKey('user.userID'), nullable=False, comment='关联的用户ID')
    commentContent = db.Column(db.Text, nullable=False, comment='评论的具体内容')
    createdDate = db.Column(db.DateTime, nullable=False, comment='评论创建的日期')
    replyUserId = db.Column(db.String(12), comment='评论回复的用户ID')
