from app import db

class File(db.Model):
    __tablename__ = 'emotionFiles'

    fileID = db.Column(db.String(12), primary_key=True)          # 文件唯一标识符
    fileName = db.Column(db.String(255), nullable=False)      # 存储文件名称
    fileType = db.Column(db.String(100), nullable=False)      # 存储文件的 MIME 类型
    fileSize = db.Column(db.BigInteger, nullable=False)       # 文件大小（字节）
    fileContent = db.Column(db.LargeBinary, nullable=False)    # 存储文件内容
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 文件创建时间

    def __repr__(self):
        return f'<File {self.fileName}>'
