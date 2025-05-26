from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import Resource

router = APIRouter()

# 喜欢资源 API 端点
@router.post("/{resource_id}/like")
def like_resource(resource_id: int, db: Session = Depends(get_db)):
    """
    增加资源的喜欢计数
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    resource.likes_count += 1
    db.commit()
    
    return {"success": True, "likes_count": resource.likes_count}

# 取消喜欢资源 API 端点
@router.post("/{resource_id}/unlike")
def unlike_resource(resource_id: int, db: Session = Depends(get_db)):
    """
    减少资源的喜欢计数
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    if resource.likes_count > 0:
        resource.likes_count -= 1
    
    db.commit()
    
    return {"success": True, "likes_count": resource.likes_count} 