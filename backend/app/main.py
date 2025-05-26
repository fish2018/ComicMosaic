from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
from typing import List, Dict
from .models.database import engine, Base, SessionLocal
from .routers import resources, auth
from .models.models import Resource, ResourceStatus
import glob
import json

# 仅创建不存在的表，保留已有数据
# (原来的 Base.metadata.drop_all(bind=engine) 行被移除)
Base.metadata.create_all(bind=engine)

# 创建初始管理员账号
db = SessionLocal()
try:
    auth.create_initial_admin(db)
    
    # 检查并恢复图片路径
    def check_and_restore_image_paths():
        print("检查图片路径数据...")
        resources_with_images = db.query(Resource).all()
        
        # 收集所有可能的图片路径
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
        upload_patterns = os.path.join(assets_dir, "uploads", "*", "*.*")
        approved_patterns = os.path.join(assets_dir, "imgs", "*", "*.*")
        
        all_images = {}
        for image_path in glob.glob(upload_patterns):
            relative_path = "/assets" + image_path.split("assets")[1]
            filename = os.path.basename(image_path)
            all_images[filename] = relative_path
            
        for image_path in glob.glob(approved_patterns):
            relative_path = "/assets" + image_path.split("assets")[1]
            filename = os.path.basename(image_path)
            all_images[filename] = relative_path
            
        print(f"找到 {len(all_images)} 个图片文件")
        
        # 检查每个资源的图片
        updated_count = 0
        for resource in resources_with_images:
            updated = False
            
            # 检查并恢复图片列表
            if resource.images:
                new_images = []
                for img_path in resource.images:
                    if not img_path.startswith("/assets"):
                        continue
                    
                    filename = os.path.basename(img_path)
                    if filename in all_images:
                        new_path = all_images[filename]
                        new_images.append(new_path)
                        updated = True
                    else:
                        new_images.append(img_path)  # 保持原路径
                
                if updated:
                    resource.images = new_images
            
            # 检查并恢复海报图片
            if resource.poster_image:
                poster_filename = os.path.basename(resource.poster_image)
                if poster_filename in all_images:
                    resource.poster_image = all_images[poster_filename]
                    updated = True
            
            if updated:
                updated_count += 1
        
        if updated_count > 0:
            db.commit()
            print(f"已恢复 {updated_count} 个资源的图片路径")
        else:
            print("无需恢复图片路径")
    
    # 启动时执行检查
    check_and_restore_image_paths()
    
finally:
    db.close()

# 创建FastAPI应用
app = FastAPI(title="资源共建平台API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# 包含路由
app.include_router(resources.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "欢迎使用资源共建平台API"} 