from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 获取backend目录路径
# 当前文件位于 backend/app/models/database.py
# 所以需要向上走两级目录
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 构建数据库文件的绝对路径
DB_PATH = os.path.join(BACKEND_DIR, "resource_hub.db")
# 创建SQLite数据库引擎，使用绝对路径
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
print(f"使用数据库: {DB_PATH}")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()

# 依赖项，用于获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 