from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..models.models import ResourceStatus

class ResourceBase(BaseModel):
    title: str  # 中文标题
    title_en: str  # 英文标题
    description: str
    resource_type: str  # 多个类型以逗号分隔
    images: Optional[List[str]] = None  # 多张图片路径的列表
    poster_image: Optional[str] = None  # 海报图片路径
    links: Optional[Dict] = None  # 资源链接，按类别分组

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    title_en: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    images: Optional[List[str]] = None
    poster_image: Optional[str] = None
    links: Optional[Dict] = None  # 资源链接，按类别分组

class Resource(ResourceBase):
    id: int
    status: ResourceStatus
    supplement: Optional[Dict] = None  # 补充内容，包含图片和链接
    original_resource_id: Optional[int] = None  # 原始资源ID
    is_supplement_approval: Optional[bool] = False  # 标记是否为补充资源审批记录
    likes_count: int = 0  # 资源被喜欢的次数
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResourceApproval(BaseModel):
    status: ResourceStatus
    field_approvals: Optional[Dict[str, bool]] = None
    field_rejections: Optional[Dict[str, bool]] = None
    approved_images: Optional[List[str]] = None
    rejected_images: Optional[List[str]] = None
    poster_image: Optional[str] = None
    notes: Optional[str] = None
    approved_links: Optional[List[Dict[str, Any]]] = None  # 已批准的链接列表，包含category和index
    rejected_links: Optional[List[Dict[str, Any]]] = None  # 已拒绝的链接列表，包含category和index

    class Config:
        json_schema_extra = {
            "example": {
                "status": "approved",
                "field_approvals": {"title": True, "description": True},
                "field_rejections": {},
                "approved_images": ["/uploads/20230101/image1.jpg"],
                "rejected_images": [],
                "poster_image": "/uploads/20230101/image1.jpg",
                "notes": "资源内容完整，审核通过",
                "approved_links": [{"category": "baidu", "index": 0}],
                "rejected_links": []
            }
        }

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class SupplementSchema(BaseModel):
    images: Optional[List[str]] = None  # 补充的图片
    links: Optional[Dict] = None  # 补充的链接
    status: ResourceStatus = ResourceStatus.PENDING  # 补充内容的审批状态
    submission_date: Optional[str] = None  # 提交日期
    approval_notes: Optional[str] = None  # 审批备注

    class Config:
        from_attributes = True 