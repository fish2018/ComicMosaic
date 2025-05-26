from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Enum
from sqlalchemy.sql import func
from .database import Base
import enum

class ResourceStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)  # 中文标题
    title_en = Column(String, index=True)  # 英文标题
    description = Column(Text)
    images = Column(JSON)  # 存储多张图片路径，JSON格式
    poster_image = Column(String, nullable=True)  # 海报图片路径
    resource_type = Column(String)  # 资源类型，存储多选值，以逗号分隔
    status = Column(Enum(ResourceStatus), default=ResourceStatus.PENDING)  # 审批状态
    hidden_from_admin = Column(Boolean, default=False)  # 是否从管理界面隐藏
    links = Column(JSON, nullable=True)  # 存储各类网盘链接，JSON格式
    original_resource_id = Column(Integer, nullable=True)  # 补充资源关联的原始资源ID
    supplement = Column(JSON, nullable=True)  # 存储补充内容，包括待审批的图片和链接
    approval_history = Column(JSON, nullable=True)  # 存储补充内容的审批历史记录
    is_supplement_approval = Column(Boolean, default=False)  # 标记是否为补充资源审批记录
    likes_count = Column(Integer, default=0, nullable=False)  # 资源被喜欢的次数
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now()) 