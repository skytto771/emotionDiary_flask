from datetime import datetime

from app import db

class User(db.Model):
    __tablename__ = 'user'

    userID = db.Column(db.String(12), primary_key=True, comment='唯一标识用户')
    username = db.Column(db.String(50), nullable=False, unique=True, comment='用户的登录名')
    email = db.Column(db.String(100), nullable=False, unique=True, comment='用户的邮箱地址')
    account = db.Column(db.String(255), nullable=False, unique=True, comment='账号')
    passwordHash = db.Column(db.String(255), nullable=False, comment='用户的密码哈希') 
    registrationDate = db.Column(db.DateTime, nullable=False, comment='用户注册的日期')
    lastLoginDate = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='用户最后登录的日期')

    avatars = db.relationship("UserAvatar", backref="user", lazy=True)