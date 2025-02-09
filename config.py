import os


class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:lzdxf20020521@localhost/emotionDB'
    # 关闭数据库修改跟踪操作 【提高性能】
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 开启输出底层执行sql语句
    SQLALCHEMY_ECHO = True


    SECRET_KEY = '9821@asd3daga'
    MAIL_SERVER = 'smtp.qq.com'  # SMTP 服务器地址
    MAIL_PORT = 465  # SMTP 端口
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = '235123797@qq.com'  # 你的邮箱用户名
    MAIL_PASSWORD = 'xnymntsplcbjcadh'  # 你的邮箱密码或应用专用密码
    MAIL_DEFAULT_SENDER = '235123797@qq.com'  # 默认发件人地址
