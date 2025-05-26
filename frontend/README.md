# 美漫资源共建平台前端

## 项目概述

美漫资源共建平台是一个专为美漫爱好者设计的资源分享与管理系统。该平台允许用户浏览、提交和评论美漫资源，管理员可以审核和管理用户提交的内容。

## 功能特点

- **资源浏览**：用户可以浏览平台上的美漫资源列表
- **资源详情**：查看特定资源的详细信息
- **资源提交**：用户可以提交新的美漫资源
- **用户登录**：支持用户认证功能
- **管理功能**：管理员可以审核和管理用户提交的资源
- **本地搜索**：支持资源搜索功能

## 技术栈

- **前端框架**：Vue.js 3.4.0
- **路由管理**：Vue Router 4.2.5
- **HTTP客户端**：Axios 1.6.5
- **构建工具**：Vite 5.0.10
- **样式框架**：Bootstrap 5.3.0
- **图标库**：Bootstrap Icons 1.10.0

## 项目结构

```
frontend/
├── assets/                # 静态资源
├── src/                   # 源代码
│   ├── assets/            # 项目资源
│   ├── components/        # 公共组件
│   │   └── LocalSearch.vue # 搜索组件
│   ├── router/            # 路由配置
│   ├── utils/             # 工具函数
│   │   ├── auth.js        # 认证相关
│   │   └── imageUtils.js  # 图片处理
│   ├── views/             # 页面组件
│   │   ├── Home.vue       # 首页
│   │   ├── Login.vue      # 登录页
│   │   ├── Admin.vue      # 管理页
│   │   ├── About.vue      # 关于页
│   │   ├── ResourceDetail.vue  # 资源详情
│   │   ├── SubmitResource.vue  # 资源提交
│   │   └── ResourceReview.vue  # 资源审核
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── index.html             # HTML模板
├── package.json           # 项目配置
└── vite.config.js         # Vite配置
```

## 安装

1. 克隆仓库
   ```
   git clone [仓库地址]
   cd [项目目录]/frontend
   ```

2. 安装依赖
   ```
   npm install
   ```

## 使用

### 开发环境

启动开发服务器：

```
npm run dev
```

开发服务器将在 http://localhost:3000 启动

### 生产环境

构建生产版本：

```
npm run build
```

预览生产构建：

```
npm run preview
```

## API 代理配置

项目已配置API代理，所有对 `/api` 的请求将被转发到 `http://127.0.0.1:8000`，这是后端服务的地址。

## 路由说明

- `/` - 首页，展示资源列表
- `/resource/:id` - 资源详情页
- `/submit` - 资源提交页
- `/login` - 用户登录页
- `/admin` - 管理员页面（需要认证）
- `/admin/resource-review/:id` - 资源审核页（需要认证）
- `/about` - 关于页面

## 注意事项

- 管理员页面需要用户登录认证
- 部分功能需要后端API支持 