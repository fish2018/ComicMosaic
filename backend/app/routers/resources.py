from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from typing import List
from datetime import datetime
from ..models.database import get_db
from ..models.models import Resource, User, ResourceStatus
from ..schemas.schemas import ResourceCreate, ResourceUpdate, Resource as ResourceSchema, ResourceApproval
from ..utils.auth import get_current_active_user, get_admin_user
from ..utils.image_utils import calculate_file_hash, move_approved_images, move_single_approved_image

router = APIRouter(
    prefix="/api/resources",
    tags=["resources"],
)

# 获取所有资源 - 普通用户只能看到已审批的资源
@router.get("/", response_model=List[ResourceSchema])
def get_resources(skip: int = 0, limit: int = 100, include_history: bool = False, db: Session = Depends(get_db), 
                  current_user: User = Depends(get_current_active_user)):
    # 管理员可以看到所有资源，但不包括已被标记为隐藏的记录
    if current_user and current_user.is_admin:
        resources = db.query(Resource).filter(Resource.hidden_from_admin == False)\
            .offset(skip).limit(limit).all()
    else:
        # 普通用户只能看到已审批的资源
        resources = db.query(Resource).filter(Resource.status == ResourceStatus.APPROVED)\
            .offset(skip).limit(limit).all()
    
    # 如果不需要包含历史记录，将 approval_history 设为 None
    if not include_history:
        for resource in resources:
            resource.approval_history = None
    
    # 确保已审批资源的海报图片路径正确指向imgs目录
    for resource in resources:
        if resource.status == ResourceStatus.APPROVED and resource.poster_image and 'uploads' in resource.poster_image:
            # 修正海报图片路径
            base_assets_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "assets")
            filename = os.path.basename(resource.poster_image)
            corrected_path = f"/assets/imgs/{resource.id}/{filename}"
            dest_path = os.path.join(base_assets_dir, "imgs", str(resource.id), filename)
            
            # 验证目标文件是否存在
            if os.path.exists(dest_path):
                resource.poster_image = corrected_path
                print(f"Corrected list poster image path to {resource.poster_image}")
            else:
                # 如果目标文件不存在，尝试从源文件复制
                src_path = os.path.join(base_assets_dir, resource.poster_image.lstrip('/assets/'))
                if os.path.exists(src_path):
                    imgs_dir = os.path.join(base_assets_dir, "imgs", str(resource.id))
                    os.makedirs(imgs_dir, exist_ok=True)
                    try:
                        print(f"Moving list poster image from {src_path} to {dest_path}")
                        shutil.copy2(src_path, dest_path)
                        resource.poster_image = corrected_path
                    except Exception as e:
                        print(f"Error moving list poster image: {e}")
    
    # 显式将SQLAlchemy模型列表转换为Pydantic模型列表
    result = []
    for resource in resources:
        result.append(ResourceSchema(
            id=resource.id,
            title=resource.title,
            title_en=resource.title_en,
            description=resource.description,
            resource_type=resource.resource_type,
            images=resource.images,
            poster_image=resource.poster_image,
            links=resource.links,
            status=resource.status,
            supplement=resource.supplement,
            original_resource_id=resource.original_resource_id,
            is_supplement_approval=resource.is_supplement_approval,
            likes_count=resource.likes_count,
            created_at=resource.created_at,
            updated_at=resource.updated_at
        ))
    
    return result

# 获取待审批的资源 - 仅管理员可访问
@router.get("/pending", response_model=List[ResourceSchema])
def get_pending_resources(skip: int = 0, limit: int = 100, 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_admin_user)):
    # 查询普通待审批资源
    resources = db.query(Resource).filter(Resource.status == ResourceStatus.PENDING)\
        .offset(skip).limit(limit).all()
    
    # 查询包含待审批补充内容的资源
    supplement_resources = db.query(Resource).filter(
        Resource.supplement.isnot(None)
    ).all()
    
    # 在Python中筛选待审批的补充内容资源
    pending_supplements = []
    for resource in supplement_resources:
        # 确保资源有supplement字段，且是字典类型
        if (resource.supplement and 
            isinstance(resource.supplement, dict) and 
            resource.supplement.get('status') == ResourceStatus.PENDING):
            # 为资源添加标记，表示它有待审批的补充内容
            resource.has_pending_supplement = True
            if resource not in resources:  # 避免重复
                pending_supplements.append(resource)
    
    # 将待审批的补充内容资源添加到结果中
    resources.extend(pending_supplements)
    
    # 显式将SQLAlchemy模型列表转换为Pydantic模型列表
    result = []
    for resource in resources:
        result.append(ResourceSchema(
            id=resource.id,
            title=resource.title,
            title_en=resource.title_en,
            description=resource.description,
            resource_type=resource.resource_type,
            images=resource.images,
            poster_image=resource.poster_image,
            links=resource.links,
            status=resource.status,
            supplement=resource.supplement,
            original_resource_id=resource.original_resource_id,
            is_supplement_approval=resource.is_supplement_approval,
            likes_count=resource.likes_count,
            created_at=resource.created_at,
            updated_at=resource.updated_at
        ))
    
    return result

# 公开API - 获取已审批的资源列表
@router.get("/public", response_model=List[ResourceSchema])
def get_public_resources(
    skip: int = 0, 
    limit: int = 100, 
    search: str = None, 
    sort_by: str = "created_at", 
    sort_order: str = "desc", 
    db: Session = Depends(get_db)
):
    query = db.query(Resource).filter(
        Resource.status == ResourceStatus.APPROVED,
        Resource.is_supplement_approval == False  # 排除补充审批记录
    )
    
    # 如果提供了搜索关键词，添加标题搜索过滤条件
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Resource.title.ilike(search_term)) |  # 搜索中文标题
            (Resource.title_en.ilike(search_term))  # 搜索英文标题
        )
    
    # 添加排序条件
    if sort_by == "likes_count":
        if sort_order.lower() == "asc":
            query = query.order_by(Resource.likes_count.asc())
        else:
            query = query.order_by(Resource.likes_count.desc())
    else:  # 默认按创建时间排序
        if sort_order.lower() == "asc":
            query = query.order_by(Resource.created_at.asc())
        else:
            query = query.order_by(Resource.created_at.desc())
    
    resources = query.offset(skip).limit(limit).all()
    
    # 确保已审批资源的海报图片路径正确指向imgs目录
    base_assets_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "assets")
    
    for resource in resources:
        if resource.poster_image:
            # 检查图片是否在 uploads 目录
            if 'uploads' in resource.poster_image:
                filename = os.path.basename(resource.poster_image)
                corrected_path = f"/assets/imgs/{resource.id}/{filename}"
                dest_path = os.path.join(base_assets_dir, "imgs", str(resource.id), filename)
                
                # 验证目标文件是否存在
                if os.path.exists(dest_path):
                    # 更新内存中的路径
                    resource.poster_image = corrected_path
                    # 同时更新数据库中的路径
                    db_resource = db.query(Resource).filter(Resource.id == resource.id).first()
                    if db_resource:
                        db_resource.poster_image = corrected_path
                        db.commit()
                    print(f"已修正公开列表中海报图片路径为: {corrected_path}")
                else:
                    # 如果目标文件不存在，尝试从源文件复制
                    src_path = os.path.join(base_assets_dir, resource.poster_image.lstrip('/assets/'))
                    if os.path.exists(src_path):
                        imgs_dir = os.path.join(base_assets_dir, "imgs", str(resource.id))
                        os.makedirs(imgs_dir, exist_ok=True)
                        try:
                            print(f"正在从 {src_path} 移动海报图片到 {dest_path}")
                            shutil.copy2(src_path, dest_path)
                            # 更新内存中的路径
                            resource.poster_image = corrected_path
                            # 同时更新数据库中的路径
                            db_resource = db.query(Resource).filter(Resource.id == resource.id).first()
                            if db_resource:
                                db_resource.poster_image = corrected_path
                                db.commit()
                        except Exception as e:
                            print(f"移动海报图片时出错: {e}")
        
        # 同样处理资源的所有图片
        if resource.images:
            corrected_images = []
            for img_path in resource.images:
                # 检查图片路径是否包含"uploads"目录
                if 'uploads' in img_path:
                    filename = os.path.basename(img_path)
                    corrected_path = f"/assets/imgs/{resource.id}/{filename}"
                    dest_path = os.path.join(base_assets_dir, "imgs", str(resource.id), filename)
                    
                    # 验证目标文件是否存在
                    if os.path.exists(dest_path):
                        print(f"已修正图片路径: {img_path} -> {corrected_path}")
                        corrected_images.append(corrected_path)
                    else:
                        # 如果目标文件不存在，尝试移动文件
                        src_path = os.path.join(base_assets_dir, img_path.lstrip('/assets/'))
                        if os.path.exists(src_path):
                            imgs_dir = os.path.join(base_assets_dir, "imgs", str(resource.id))
                            os.makedirs(imgs_dir, exist_ok=True)
                            try:
                                print(f"正在从 {src_path} 移动图片到 {dest_path}")
                                shutil.copy2(src_path, dest_path)
                                corrected_images.append(corrected_path)
                            except Exception as e:
                                print(f"移动图片时出错: {e}")
                                corrected_images.append(img_path)  # 保留原路径
                        else:
                            print(f"源文件不存在: {src_path}")
                            corrected_images.append(img_path)  # 保留原路径
                else:
                    corrected_images.append(img_path)
            
            # 只有当存在修改时才更新数据库
            if any('uploads' in img for img in resource.images):
                # 更新内存中的图片列表
                resource.images = corrected_images
                # 同时更新数据库中的图片列表
                db_resource = db.query(Resource).filter(Resource.id == resource.id).first()
                if db_resource:
                    db_resource.images = corrected_images
                    db.commit()
    
    # 显式将SQLAlchemy模型列表转换为Pydantic模型列表
    result = []
    for resource in resources:
        result.append(ResourceSchema(
            id=resource.id,
            title=resource.title,
            title_en=resource.title_en,
            description=resource.description,
            resource_type=resource.resource_type,
            images=resource.images,
            poster_image=resource.poster_image,
            links=resource.links,
            status=resource.status,
            supplement=resource.supplement,
            original_resource_id=resource.original_resource_id,
            is_supplement_approval=resource.is_supplement_approval,
            likes_count=resource.likes_count,
            created_at=resource.created_at,
            updated_at=resource.updated_at
        ))
    
    return result

# 获取单个资源
@router.get("/{resource_id}", response_model=ResourceSchema)
def get_resource(resource_id: int, is_admin_view: bool = False, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if resource is None:
        raise HTTPException(status_code=404, detail="资源未找到")
    
    # 只有在公开页面访问时（非管理页面），才重定向补充审批记录到原始资源
    if not is_admin_view and resource.is_supplement_approval and resource.original_resource_id:
        original_resource = db.query(Resource).filter(Resource.id == resource.original_resource_id).first()
        if original_resource:
            print(f"公开页面请求补充资源审批记录 {resource_id}，重定向到原始资源 {resource.original_resource_id}")
            resource = original_resource
        else:
            print(f"补充资源审批记录 {resource_id} 的原始资源 {resource.original_resource_id} 未找到")
    
    # 确保审批通过的资源不会显示被拒绝的链接
    if resource.status == ResourceStatus.APPROVED and hasattr(resource, 'links') and resource.links:
        # 创建一个只包含已批准链接的新字典
        filtered_links = {}
        
        # 对每个类别的链接进行过滤
        for category, links in resource.links.items():
            if links:  # 确保该类别有链接
                # 保留链接
                filtered_links[category] = links
        
        # 替换原始的链接对象
        resource.links = filtered_links
        
        print(f"Filtered links for resource {resource_id}: {resource.links}")
    
    # 确保图片路径指向imgs目录而不是uploads目录
    if resource.status == ResourceStatus.APPROVED and hasattr(resource, 'images') and resource.images:
        corrected_images = []
        base_assets_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "assets")
        
        for img_path in resource.images:
            # 检查图片路径是否包含"uploads"目录
            if 'uploads' in img_path:
                # 创建正确的imgs目录路径
                filename = os.path.basename(img_path)
                corrected_path = f"/assets/imgs/{resource_id}/{filename}"
                
                # 验证目标文件是否存在
                dest_path = os.path.join(base_assets_dir, "imgs", str(resource_id), filename)
                if os.path.exists(dest_path):
                    print(f"Corrected image path from {img_path} to {corrected_path}")
                    corrected_images.append(corrected_path)
                else:
                    # 如果目标文件不存在，尝试移动文件
                    src_path = os.path.join(base_assets_dir, img_path.lstrip('/assets/'))
                    if os.path.exists(src_path):
                        imgs_dir = os.path.join(base_assets_dir, "imgs", str(resource_id))
                        os.makedirs(imgs_dir, exist_ok=True)
                        try:
                            print(f"Moving image from {src_path} to {dest_path}")
                            shutil.copy2(src_path, dest_path)
                            corrected_images.append(corrected_path)
                        except Exception as e:
                            print(f"Error moving image: {e}")
                            corrected_images.append(img_path)  # 保留原路径
                    else:
                        print(f"Source file does not exist: {src_path}")
                        corrected_images.append(img_path)  # 保留原路径
            else:
                corrected_images.append(img_path)
        
        # 更新资源图片路径
        resource.images = corrected_images
        
        # 如果海报图片也是指向uploads目录，修正它
        if resource.poster_image and 'uploads' in resource.poster_image:
            filename = os.path.basename(resource.poster_image)
            dest_path = os.path.join(base_assets_dir, "imgs", str(resource_id), filename)
            corrected_poster_path = f"/assets/imgs/{resource_id}/{filename}"
            
            # 验证目标文件是否存在
            if os.path.exists(dest_path):
                resource.poster_image = corrected_poster_path
                print(f"Corrected poster image path to {resource.poster_image}")
            else:
                # 如果目标文件不存在，尝试移动文件
                src_path = os.path.join(base_assets_dir, resource.poster_image.lstrip('/assets/'))
                if os.path.exists(src_path):
                    try:
                        print(f"Moving poster image from {src_path} to {dest_path}")
                        shutil.copy2(src_path, dest_path)
                        resource.poster_image = corrected_poster_path
                    except Exception as e:
                        print(f"Error moving poster image: {e}")
                        # 保留原路径
    
    # 显式将SQLAlchemy模型转换为Pydantic模型
    return ResourceSchema(
        id=resource.id,
        title=resource.title,
        title_en=resource.title_en,
        description=resource.description,
        resource_type=resource.resource_type,
        images=resource.images,
        poster_image=resource.poster_image,
        links=resource.links,
        status=resource.status,
        supplement=resource.supplement,
        original_resource_id=resource.original_resource_id,
        is_supplement_approval=resource.is_supplement_approval,
        likes_count=resource.likes_count,
        created_at=resource.created_at,
        updated_at=resource.updated_at
    )

# 创建新资源 - 匿名用户可提交，状态默认为待审批
@router.post("/", response_model=ResourceSchema)
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    # 确保links字段格式正确
    links = resource.links
    if links:
        print(f"Resource submitted with links: {links}")
    else:
        links = {}
        print("No links provided in resource submission")
    
    db_resource = Resource(
        title=resource.title,
        title_en=resource.title_en,
        description=resource.description,
        images=resource.images,
        resource_type=resource.resource_type,
        status=ResourceStatus.PENDING,
        links=links  # 显式设置links字段
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    
    # 显式将SQLAlchemy模型转换为Pydantic模型
    return ResourceSchema(
        id=db_resource.id,
        title=db_resource.title,
        title_en=db_resource.title_en,
        description=db_resource.description,
        resource_type=db_resource.resource_type,
        images=db_resource.images,
        poster_image=db_resource.poster_image,
        links=db_resource.links,
        status=db_resource.status,
        supplement=db_resource.supplement,
        original_resource_id=db_resource.original_resource_id,
        is_supplement_approval=db_resource.is_supplement_approval,
        likes_count=db_resource.likes_count,
        created_at=db_resource.created_at,
        updated_at=db_resource.updated_at
    )

# 更新资源 - 仅管理员可更新
@router.put("/{resource_id}", response_model=ResourceSchema)
def update_resource(
    resource_id: int,
    resource_update: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="资源未找到")
    
    # 更新非空字段
    update_data = resource_update.dict(exclude_unset=True)
    
    # 特殊处理links字段，确保链接格式正确
    if 'links' in update_data:
        links = update_data['links']
        print(f"处理资源链接更新: {links}")
        
        # 验证链接格式
        valid_categories = [
            "magnet", "ed2k", "uc", "mobile", "tianyi", "quark", 
            "115", "aliyun", "pikpak", "baidu", "123", "online", "others"
        ]
        
        standardized_links = {}
        
        # 遍历每个链接类别
        for category, category_links in links.items():
            if category not in valid_categories:
                print(f"警告: 忽略无效链接类别 '{category}'")
                continue
            
            standardized_links[category] = []
            
            # 处理该类别下的所有链接
            for link in category_links:
                # 确保每个链接项都是完整的对象
                if isinstance(link, str):
                    # 如果是字符串，转换为对象格式
                    standardized_links[category].append({
                        "url": link,
                        "password": "",
                        "note": ""
                    })
                elif isinstance(link, dict):
                    # 验证必要的URL字段
                    if "url" not in link or not link["url"]:
                        print(f"警告: 忽略缺少URL的链接项: {link}")
                        continue
                    
                    # 创建标准化的链接对象
                    standardized_links[category].append({
                        "url": link["url"],
                        "password": link.get("password", ""),
                        "note": link.get("note", "")
                    })
        
        # 更新links字段为标准格式
        update_data["links"] = standardized_links
        print(f"标准化后的链接: {standardized_links}")
    
    # 应用所有更新
    for key, value in update_data.items():
        setattr(db_resource, key, value)
    
    try:
        db.commit()
        db.refresh(db_resource)
        print(f"资源 {resource_id} 更新成功")
    except Exception as e:
        db.rollback()
        print(f"更新资源时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="服务器处理更新请求时出错")
    
    # 显式将SQLAlchemy模型转换为Pydantic模型
    return ResourceSchema(
        id=db_resource.id,
        title=db_resource.title,
        title_en=db_resource.title_en,
        description=db_resource.description,
        resource_type=db_resource.resource_type,
        images=db_resource.images,
        poster_image=db_resource.poster_image,
        links=db_resource.links,
        status=db_resource.status,
        supplement=db_resource.supplement,
        original_resource_id=db_resource.original_resource_id,
        is_supplement_approval=db_resource.is_supplement_approval,
        likes_count=db_resource.likes_count,
        created_at=db_resource.created_at,
        updated_at=db_resource.updated_at
    )

# 审批资源 - 仅管理员可审批
@router.put("/{resource_id}/approve", response_model=ResourceSchema)
async def approve_resource(
    resource_id: int,
    approval: ResourceApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="资源未找到")

    # 检查是否为补充资源审批
    has_supplement = hasattr(db_resource, 'supplement') and db_resource.supplement
    is_supplement = False
    
    if has_supplement and db_resource.supplement.get('status') == ResourceStatus.PENDING:
        is_supplement = True
        print(f"检测到补充资源审批，资源ID: {resource_id}")
        print(f"补充内容: {db_resource.supplement}")
    
    # 检查是否为传统的补充资源（旧数据兼容）
    is_legacy_supplement = hasattr(db_resource, 'original_resource_id') and db_resource.original_resource_id is not None
    original_resource = None
    
    if is_legacy_supplement and approval.status == ResourceStatus.APPROVED:
        # 获取原始资源
        original_resource = db.query(Resource).filter(
            Resource.id == db_resource.original_resource_id
        ).first()
        
        if not original_resource:
            raise HTTPException(status_code=404, detail="原始资源未找到，无法完成补充")
    
    # 更新状态（对于非补充内容审批）
    if not is_supplement:
        db_resource.status = approval.status
    
    # 记录审批笔记（如果有）
    if approval.notes:
        if is_supplement:
            # 将笔记添加到补充内容中
            db_resource.supplement['approval_notes'] = approval.notes
        else:
            # 将笔记添加到描述的末尾
            db_resource.description += f"\n\n管理员审批意见: {approval.notes}"
    
    # 如果审批通过，则处理已批准的图片和链接
    if approval.status == ResourceStatus.APPROVED:        
        # 处理已批准的图片
        images = db_resource.images.copy() if db_resource.images else [] # 原始资源图片列表
        add_images = []
        if approval.approved_images:
            if is_supplement:                
                # 移动已批准的图片
                for img in approval.approved_images:
                    # 移动该图片到已批准目录
                    new_path = move_single_approved_image(resource_id, img)
                    images.append(new_path)
                    add_images.append(new_path)
                    print(f"已移动批准的补充图片: {img} -> {new_path}")

                print(f"最终批准的图片列表: {images}")
                
                # 将批准的图片添加到原资源的图片列表中                
                # 确保不添加重复的图片
                images = list(set(images))
                db_resource.images = images
                db.commit()
                print(f"已将图片变更提交到数据库")
                
                # 如果没有设置海报图片，使用第一张批准的图片作为海报
                if not db_resource.poster_image and new_images:
                    db_resource.poster_image = new_images[0]
                    print(f"自动设置第一张批准图片为海报: {db_resource.poster_image}")
                    db.commit()
            else:
                # 获取原始图片列表（非补充模式）
                original_images = db_resource.images or []
                
                # 创建新的图片路径列表
                new_images = []
                
                # 移动已批准的图片
                for img in approval.approved_images:
                    if img in original_images:
                        # 移动该图片到已批准目录
                        try:
                            new_path = move_single_approved_image(resource_id, img)
                            new_images.append(new_path)
                            print(f"Moved approved image from {img} to {new_path}")
                        except Exception as e:
                            print(f"Error moving approved image: {e}")
                
                # 更新资源的图片列表，仅包含已批准的图片
                db_resource.images = new_images
                
                # 设置海报图片
                if approval.poster_image:
                    # 确保选择的海报图片在已批准的图片中
                    if approval.poster_image in original_images:
                        # 找到对应的新路径
                        for old_path, new_path in zip(original_images, new_images):
                            if old_path == approval.poster_image:
                                db_resource.poster_image = new_path
                                break
                
                # 如果没有设置海报图片或者设置的海报图片不在批准列表中，使用第一张批准的图片作为海报
                if (not db_resource.poster_image or not approval.poster_image) and new_images:
                    db_resource.poster_image = new_images[0]
                    print(f"Automatically setting first approved image as poster: {db_resource.poster_image}")
        
        # 处理已批准的链接
        if is_supplement:
            # 处理前端传递的批准链接 - 修改这部分代码以适应前端传递的数据格式
            if hasattr(approval, 'approved_links') and approval.approved_links:
                links = db_resource.links.copy() if db_resource.links else {}
                links = {
                    "magnet": links.get('magnet', []),
                    "ed2k": links.get('ed2k', []),
                    "uc": links.get('uc', []),
                    "mobile": links.get('mobile', []),
                    "tianyi": links.get('tianyi', []),
                    "quark": links.get('quark', []),
                    "115": links.get('115', []),
                    "aliyun": links.get('aliyun', []),
                    "pikpak": links.get('pikpak', []),
                    "baidu": links.get('baidu', []),
                    "123": links.get('123', []),
                    "online": links.get('online', []),
                    "others": links.get('others', [])
                }

                for link_info in approval.approved_links:
                    # {category: "xx", url: "xxx", password: "xx", note: "xx"}
                    category = link_info.get('category')
                    url = link_info.get('url')
                    password = link_info.get('password', '')
                    note = link_info.get('note', '')
                    
                    if not category or not url:
                        print(f"警告: 链接信息不完整，跳过: {link_info}")
                        continue
                    
                    print(f"处理批准的链接: 分类={category}, URL={url}")
                    
                    # 确保目标分类存在
                    category_list = links.get(category, [])
                    
                    # 构建链接对象
                    link_obj = {
                        "url": url,
                        "password": password if password else "",
                        "note": note if note else ""
                    }
                    
                    category_list.append(link_obj)
                    links[category] = category_list

                try:
                    print(f"更新后的资源最终链接: {links}")
                    db_resource.links = links
                    db.commit()
                    print(f"已将链接变更提交到数据库")
                    db.refresh(db_resource)
                except Exception as e:
                    print(f"处理批准链接时出错: {str(e)}")
                    import traceback
                    traceback.print_exc()
            

            # 创建一个新的独立资源记录来保存这次补充审批的结果
            supplement_record = Resource(
                title=db_resource.title,
                title_en=db_resource.title_en,
                resource_type=db_resource.resource_type,
                status=approval.status,
                hidden_from_admin=False,  # 确保可以在管理面板中看到
                original_resource_id=db_resource.id,  # 关联原始资源
                is_supplement_approval=True,  # 标记为补充资源审批
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 添加审批备注
            if approval.notes:
                supplement_record.description = f"补充内容审批 - {approval.notes}"
            else:
                supplement_record.description = "补充内容审批"
            
            # 保存补充的图片和链接信息
            supplement_record.images = add_images
            supplement_record.links = db_resource.supplement.get('links', {})
            
            # 添加到数据库
            db.add(supplement_record)
            
            # 确保补充审批记录被立即保存到数据库
            db.commit()
            print(f"已将补充审批记录 {supplement_record.id} 提交到数据库")
            
            # 如果审批通过，合并补充内容到原资源并清空supplement
            if approval.status == ResourceStatus.APPROVED:
                # 清空当前的补充内容，表示已处理完毕
                db_resource.supplement = None
                print(f"补充内容已批准并合并到资源 {resource_id}，同时创建了审批记录")
            else:
                # 如果拒绝，保留补充内容但更新状态
                db_resource.supplement['status'] = approval.status
                print(f"补充内容已被拒绝 {resource_id}，同时创建了审批记录")
                db.commit()
            print(f"已将更新后的资源信息提交到数据库: 图片数量={len(db_resource.images or [])}, 链接类别数量={len(db_resource.links or {})}")
        else:
            print("Resource has no approved images")

    else:
        print("Resource has no approved status")
    
    db.commit()
    db.refresh(db_resource)
    # 显式将SQLAlchemy模型转换为Pydantic模型
    return ResourceSchema(
        id=db_resource.id,
        title=db_resource.title,
        title_en=db_resource.title_en,
        description=db_resource.description,
        resource_type=db_resource.resource_type,
        images=db_resource.images,
        poster_image=db_resource.poster_image,
        links=db_resource.links,
        status=db_resource.status,
        supplement=db_resource.supplement,
        original_resource_id=db_resource.original_resource_id,
        is_supplement_approval=db_resource.is_supplement_approval,
        likes_count=db_resource.likes_count,
        created_at=db_resource.created_at,
        updated_at=db_resource.updated_at
    )

# 删除资源 - 仅管理员可删除
@router.delete("/{resource_id}", status_code=204)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="资源未找到")
    
    db.delete(db_resource)
    db.commit()
    return {"status": "success"}

# 删除审批记录 - 仅管理员可删除记录，但保留资源
@router.delete("/{resource_id}/record", status_code=204)
def delete_approval_record(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="资源记录未找到")
    
    # 将资源从审批记录中"隐藏"，而不是真正删除
    # 这里我们通过设置一个标记字段来实现
    db_resource.hidden_from_admin = True
    db.commit()
    db.refresh(db_resource)
    
    return {"status": "success"}

# 上传图片 - 匿名用户可上传，使用哈希命名文件
@router.post("/upload-images/")
async def upload_images(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 获取当前日期，格式为YYYYMMDD
    today = datetime.now().strftime("%Y%m%d")
    
    # 确保uploads目录和日期子目录存在
    base_upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "assets", "uploads")
    upload_dir = os.path.join(base_upload_dir, today)
    
    # 如果目录不存在，创建它
    os.makedirs(upload_dir, exist_ok=True)
    
    # 计算文件的哈希值用于命名
    file_hash = calculate_file_hash(file.file)
    
    # 获取文件扩展名
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    # 创建以哈希值命名的文件名
    file_name = f"{file_hash}{file_extension}"
    file_path = os.path.join(upload_dir, file_name)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        # 重置文件指针到开头
        file.file.seek(0)
        shutil.copyfileobj(file.file, buffer)
    
    # 返回相对路径，以便前端可以访问
    return {"filename": f"/assets/uploads/{today}/{file_name}"}

# 补充资源图片 - 匿名用户可提交
@router.put("/{resource_id}/supplement", response_model=ResourceSchema)
async def supplement_resource(
    resource_id: int,
    supplement: dict,
    db: Session = Depends(get_db)
):
    # 检查资源是否存在
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="资源未找到")
    
    # 检查资源是否已经审批通过
    if db_resource.status != ResourceStatus.APPROVED:
        raise HTTPException(status_code=400, detail="只能补充已审批通过的资源")
    
    # 获取新的图片列表和链接
    new_images = supplement.get('images', [])
    new_links = supplement.get('links', {})
    
    # 确保links格式正确
    if new_links:
        print(f"Supplement submitted with links: {new_links}")
    else:
        new_links = {}
        print("No links provided in supplement submission")
    
    # 在原资源上添加supplement字段，存储待审批的补充内容
    # 如果已经有supplement字段，合并新的补充内容
    if not hasattr(db_resource, 'supplement') or not db_resource.supplement:
        db_resource.supplement = {}
    
    # 更新补充内容
    db_resource.supplement = {
        'images': new_images,
        'links': new_links,
        'status': ResourceStatus.PENDING,  # 补充内容待审批
        'submission_date': datetime.now().isoformat()
    }
    
    db.commit()
    db.refresh(db_resource)
    
    # 显式将SQLAlchemy模型转换为Pydantic模型
    return ResourceSchema(
        id=db_resource.id,
        title=db_resource.title,
        title_en=db_resource.title_en,
        description=db_resource.description,
        resource_type=db_resource.resource_type,
        images=db_resource.images,
        poster_image=db_resource.poster_image,
        links=db_resource.links,
        status=db_resource.status,
        supplement=db_resource.supplement,
        original_resource_id=db_resource.original_resource_id,
        is_supplement_approval=db_resource.is_supplement_approval,
        likes_count=db_resource.likes_count,
        created_at=db_resource.created_at,
        updated_at=db_resource.updated_at
    )

# 获取待审批的补充内容 - 用于审批界面
@router.get("/{resource_id}/supplement", response_model=dict)
def get_resource_supplement(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="资源未找到")
    
    # 检查是否有补充内容
    if not hasattr(db_resource, 'supplement') or not db_resource.supplement:
        raise HTTPException(status_code=404, detail="该资源没有待审批的补充内容")
    
    # 返回原始资源信息和补充内容
    return {
        'resource': {
            'id': db_resource.id,
            'title': db_resource.title,
            'title_en': db_resource.title_en,
            'resource_type': db_resource.resource_type,
            'status': db_resource.status,
        },
        'supplement': db_resource.supplement
    }

# 获取有待审批补充内容的资源列表 - 仅管理员可访问
@router.get("/pending-supplements", response_model=List[ResourceSchema])
def get_pending_supplement_resources(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    # 查询所有包含补充内容的资源
    resources_with_supplement = db.query(Resource).filter(
        Resource.supplement.isnot(None)  # 有supplement字段
    ).all()
    
    # 在Python中筛选待审批的补充内容
    pending_resources = [
        resource for resource in resources_with_supplement
        if resource.supplement and isinstance(resource.supplement, dict) and resource.supplement.get('status') == ResourceStatus.PENDING
    ]
    
    # 应用分页
    start = skip
    end = skip + limit
    paginated_resources = pending_resources[start:end]
    
    # 显式将SQLAlchemy模型列表转换为Pydantic模型列表
    result = []
    for resource in paginated_resources:
        result.append(ResourceSchema(
            id=resource.id,
            title=resource.title,
            title_en=resource.title_en,
            description=resource.description,
            resource_type=resource.resource_type,
            images=resource.images,
            poster_image=resource.poster_image,
            links=resource.links,
            status=resource.status,
            supplement=resource.supplement,
            original_resource_id=resource.original_resource_id,
            is_supplement_approval=resource.is_supplement_approval,
            likes_count=resource.likes_count,
            created_at=resource.created_at,
            updated_at=resource.updated_at
        ))
    
    return result

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