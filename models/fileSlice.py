from app import db

class FileSlice(db.Model):
    __tablename__ = 'fileSlices'  # 与数据库中的切片表对应

    sliceID = db.Column(db.String(12), primary_key=True)  # 切片ID，主键
    fileID = db.Column(db.String(12), db.ForeignKey('emotionFiles.fileID'), nullable=False)  # 所属文件的ID
    sliceIndex = db.Column(db.Integer, nullable=False)  # 切片索引
    sliceContent = db.Column(db.LargeBinary, nullable=False)  # 切片内容
    sliceSize = db.Column(db.BigInteger, nullable=False)  # 切片大小，以字节为单位
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间


