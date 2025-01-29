from app import db

class Resource(db.Model):
    __tablename__ = 'resource'

    resourceID = db.Column(db.String(12), primary_key=True, comment='资源的唯一标识')
    resourceType = db.Column(db.String(50), nullable=False, comment='资源的类型')
    resourceLink = db.Column(db.String(255), nullable=False, comment='资源的访问链接或文件路径')
