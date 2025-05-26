from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.models import User
from ..schemas.schemas import Token, User as UserSchema, UserCreate, PasswordUpdate
from ..utils.auth import (
    authenticate_user, create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash,
    get_current_active_user, get_admin_user
)

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 创建初始管理员账号函数
def create_initial_admin(db: Session):
    # 检查是否已经有用户
    if db.query(User).count() > 0:
        return
    
    # 创建默认管理员账号
    default_username = "admin"
    default_password = "admin123"  # 默认密码，应该在首次登录后修改
    
    hashed_password = get_password_hash(default_password)
    db_user = User(
        username=default_username, 
        hashed_password=hashed_password, 
        is_admin=True
    )
    db.add(db_user)
    db.commit()
    print(f"已创建初始管理员账号: {default_username}，默认密码: {default_password}")
    return db_user

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.post("/change-password", response_model=UserSchema)
async def change_password(
    password_update: PasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not authenticate_user(db, current_user.username, password_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码不正确"
        )
    
    # 更新密码
    hashed_password = get_password_hash(password_update.new_password)
    current_user.hashed_password = hashed_password
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user 