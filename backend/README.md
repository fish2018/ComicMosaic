# 资源共建平台后端

这是资源共建平台的后端服务，基于FastAPI和SQLAlchemy开发，提供资源管理、用户认证等API接口。

## 目录结构

```
backend/
├── app/                  # 主应用目录
│   ├── main.py          # 应用入口文件
│   ├── models/          # 数据模型
│   │   ├── database.py  # 数据库配置
│   │   └── models.py    # 数据表模型
│   ├── routers/         # 路由模块
│   │   ├── auth.py      # 认证相关路由
│   │   └── resources.py # 资源相关路由
│   ├── schemas/         # Pydantic模型
│   └── utils/           # 工具函数
├── resource_hub.db      # SQLite数据库文件
├── requirements.txt     # 项目依赖
├── run.py               # 启动脚本
└── venv/                # 虚拟环境（不包含在版本控制中）
```

## 环境要求

- Python 3.8+
- 依赖项见 `requirements.txt`

## 安装与运行

### 安装

1. 创建并激活Python虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

### 运行

启动开发服务器：

```bash
python run.py
```

服务将在 `http://0.0.0.0:8000` 启动，支持热重载。

## 数据库配置

项目使用SQLite数据库，配置在 `app/models/database.py` 中。数据库文件为 `resource_hub.db`。

### 自动创建数据库

如果 `resource_hub.db` 文件被删除，系统在启动时会自动：
1. 创建新的数据库文件
2. 根据模型定义创建所有表结构
3. 创建初始管理员账号

无需手动执行数据库迁移命令。

## API接口

### 认证相关

- `POST /api/auth/token` - 获取访问令牌（登录）
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/register` - 注册新用户

### 资源管理

- `GET /api/resources/` - 获取资源列表
- `POST /api/resources/` - 创建新资源
- `GET /api/resources/{id}` - 获取单个资源详情
- `PUT /api/resources/{id}` - 更新资源
- `DELETE /api/resources/{id}` - 删除资源
- `POST /api/resources/upload-images/` - 上传资源图片
- `GET /api/resources/admin/` - 管理员获取待审核资源
- `POST /api/resources/{id}/approve` - 审核通过资源
- `POST /api/resources/{id}/reject` - 拒绝资源
- `GET /api/resources/supplements/` - 获取补充资源列表

## 安全与认证

系统使用JWT（JSON Web Token）进行身份验证。管理员账号在首次启动时自动创建，默认认证在 `app/routers/auth.py` 中配置。

## 文件上传

支持图片上传，文件保存在项目根目录下的 `assets/uploads/` 目录中。文件路径会自动保存到数据库中的相应字段。

## 错误处理

系统实现了统一的错误处理机制，会返回合适的HTTP状态码和错误消息。 