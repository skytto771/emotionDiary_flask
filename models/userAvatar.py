from app import db


class UserAvatar(db.Model):
    __tablename__ = 'userAvatar'

    avatarID = db.Column(db.String(12), primary_key=True, comment='唯一标识用户头像')
    userID = db.Column(db.String(12), db.ForeignKey('user.userID'), nullable=False, comment='与用户表的关联ID')
    fileID = db.Column(db.String(12), db.ForeignKey('emotionFiles.fileID'), nullable=False, comment='与文件表的关联ID')
    avatarUrl = db.Column(db.String(255), nullable=False, comment='头像的URL地址')