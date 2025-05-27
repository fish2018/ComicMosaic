# ComicMosaic
一个开源美漫共建平台，不同用户可以自由提交动漫信息(标题、类型、简介、图片、资源链接)，像马赛克一样，由多方贡献拼凑成完整资源。当然程序本身是通用的，用来做电影、剧集、综艺等等都可以。  

正式上线地址：https://dm.xueximeng.com/  
套CF CDN地址：https://mm.252035.xyz/

如果喜欢，点个star  

---

## 适配移动端样式
移动端也可以更好的体验美漫共建小站了

![移动端|237x499](docs/1.gif)

## 首页
![image|690x397](docs/2.jpg)

可以根据资源中文名、英文名、简介进行搜索
![首页|690x392](docs/3.gif)

## 详情页
![image|690x398](docs/4.jpg)

可以切换查看图片，选择网盘标签，一键复制网盘链接密码
![详情页|690x392](docs/5.gif)

## 关于本站
![关于|690x392](docs/6.gif)

## 提交资源
这个才是资源共建平台的核心，点击右上角的'提交资源'，用户可以随意提交自己喜欢的动漫资源，如果网站还不存该美漫时，会是一个新建资源的表单，需要填写中文名、英文名、类型、简介等基础信息。提交后，要等管理员在后台审批完才会在首页显示

### 提交-新建资源
![image|690x384](docs/7.jpg)  
![image|690x379](docs/8.jpg)  

网盘链接和图片都可以提交多个
![提交资源|690x392](docs/9.gif)

### 提交-补充资源
顾名思义，就是对已经存在的动漫资源补充一些信息，主要是图片、资源链接
补充提交有2个入口，一个是右上角的'提交资源'，搜索已经存在的动漫名，然后选择确认即可
![image|690x396](docs/10.jpg)  

![补充资源|690x392](docs/11.gif)

从资源详情页点击'补充资源'按钮，不用自己再搜索选择了，自动绑定对应的动漫
![详情页补充|690x392](docs/12.gif)

## 管理员登录
不用多说了，就是输入账号密码，初始密码登录后可修改

![image|690x401](docs/13.jpg)

## 管理控制台
主要用于审批用户提交的资源

![image|690x398](docs/14.jpg)

审批用户提交的资源
![后台审批|690x391](docs/15.gif)

## 资源编辑(管理员权限)
管理员在动漫详情页面，可以进行编辑，修改中英文标题、简介、类型、图片增删、海报设置、修改添加资源链接等
![image|690x365](docs/16.jpg)  
![image|690x303](docs/17.jpg)  

![详情编辑|690x391](docs/18.gif)

## 新增喜欢按钮
在详情页可以点击喜欢
![image|690x370](docs/19.jpg)
首页可以根据喜欢数量排序，默认按最新发布排序
![image|690x397](docs/20.jpg)

---

# 美漫资源共建平台部署

本教程将指导您如何将前端和后端代码部署到 `/home/work/dongman` 目录，并使用nginx配置同一个域名 `https://dm.xueximeng.com`。

## 一、目录结构

首先创建所需的目录结构：

```bash
/home/work/dongman/
├── assets/                   # 资源文件目录（用户上传的图片）
│   ├── imgs/
│   └── uploads/
├── backend/                  # 后端代码目录
│   ├── app/
│   │   ├── main.py           # FastAPI主应用入口点
│   │   ├── models/
│   │   │   ├── database.py   # 数据库连接设置
│   │   │   └── models.py     # SQLAlchemy数据模型
│   │   ├── routers/
│   │   │   ├── auth.py       # 认证相关路由
│   │   │   └── resources.py  # 资源管理路由
│   │   ├── schemas/
│   │   │   └── schemas.py    # Pydantic模型
│   │   └── utils/
│   │       ├── __init__.py   # Python包初始化文件
│   │       ├── auth.py       # 认证工具函数
│   │       └── image_utils.py # 图像处理工具
│   ├── resource_hub.db       # SQLite数据库文件
│   ├── requirements.txt      # Python依赖项
│   ├── run.py                # 应用启动脚本
│   └── README.md             # 后端文档
├── frontend/                 # 前端代码目录
│   ├── assets/               # 静态资源
│   ├── node_modules/         # npm包
│   ├── src/
│   │   ├── assets/           # 前端静态资源
│   │   ├── components/
│   │   │   └── LocalSearch.vue # 本地搜索组件
│   │   ├── router/
│   │   │   └── index.js      # Vue路由配置
│   │   ├── utils/
│   │   │   ├── auth.js       # 认证相关工具
│   │   │   └── imageUtils.js # 图像处理工具
│   │   ├── views/
│   │   │   ├── About.vue     # 关于页面
│   │   │   ├── Admin.vue     # 管理员控制台
│   │   │   ├── Home.vue      # 首页
│   │   │   ├── Login.vue     # 登录页
│   │   │   ├── ResourceDetail.vue # 资源详情页
│   │   │   ├── ResourceReview.vue # 资源审核页
│   │   │   └── SubmitResource.vue # 资源提交页面
│   │   ├── App.vue           # 根组件
│   │   └── main.js           # Vue应用入口点
│   ├── .eslintrc.json        # ESLint配置
│   ├── index.html            # HTML入口
│   ├── package-lock.json     # npm依赖锁定
│   ├── package.json          # npm项目配置
│   ├── README.md             # 前端文档
│   └── vite.config.js        # Vite构建配置
├── migrations/               # 数据库迁移脚本
└── prompt.md                 # 项目概述文档
``` 

## 二、前端部署

### 构建前端代码

#### 进入前端代码目录
```
cd /home/work/dongman/frontend
```
#### 安装依赖
```
npm install
```
#### 创建生产环境变量文件
```
cat > .env.production << EOL
NODE_ENV=production
VUE_APP_BASE_API=/api
EOL
```

#### 修改`vite.config.js`文件
```
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// 其他导入...

export default defineConfig({
  plugins: [vue()],
  base: '/static/', // 修改静态资源基础路径
  // 其他配置...
})
```
完整配置
```
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  base: '/static/', // 修改静态资源基础路径
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/assets': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}) 
```

#### 编译
```
npm i && npm run build
```

构建完成后，将在 `/home/work/dongman/frontend/dist` 目录中生成静态文件。

## 三、后端部署

### 安装后端依赖

#### 进入后端代码目录
```
cd /home/work/dongman/backend
```
#### 创建并激活虚拟环境
```
python -m venv venv
source venv/bin/activate
```
#### 安装依赖
```
pip install -r requirements.txt
```

## 四、Supervisor 配置

配置 Supervisor 来管理后端应用：

#### 创建 supervisor 配置文件
```
sudo nano /etc/supervisor/conf.d/dongman.conf
```

填入以下内容：

```ini
[program:dm]
command=python3 /root/work/dongman/backend/run.py 
directory=/home/work/dongman/backend        ; 项目的文件夹路径
autostart=true                              ; 是否在 Supervisor 启动时自动启动该程序
autorestart=true                            ; 程序退出后是否自动重启
startsecs=5                                 ; 程序启动需要的秒数
startretries=3                              ; 启动失败后的重试次数
exitcodes=0                                 ; 程序正常退出的退出码
stopwaitsecs=10                             ; 程序停止等待的秒数
stopasgroup=true                            ; 是否向进程组发送停止信号
killasgroup=true                            ; 是否向进程组发送杀死信号
redirect_stderr=true                        ; 是否将 stderr 重定向到 stdout
stdout_logfile=/home/work/logs/dongman.log
stdout_logfile_maxbytes=50MB                ; 标准输出日志文件的最大字节数
stdout_logfile_backups=10                   ; 保留的日志文件备份数量
```

重新加载 supervisor 配置：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start dm
```

## 五、Nginx 配置

### 1. 安装 Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. 配置 Nginx

```bash
sudo vi /etc/nginx/conf.d/dongman.conf
```

填入以下配置：

```nginx
server {
    listen 80;
    server_name dm.xueximeng.com;
    
    # 重定向 HTTP 请求到 HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name dm.xueximeng.com;
    
    # SSL 配置
    ssl_certificate /etc/letsencrypt/live/xueximeng.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/xueximeng.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    
    # 安全头部
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";

    # 上传的资源文件
    location /assets/ {
        alias /home/work/dongman/assets/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # 前端静态资源 - 使用不同的路径
    location /static/assets/ {
        alias /home/work/dongman/frontend/dist/assets/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        access_log off;
    }

    # API 请求转发到后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_redirect off;
        proxy_read_timeout 120s;
    }
    
    # 前端静态文件
    location / {
        root /home/work/dongman/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # 缓存策略
        location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 30d;
            add_header Cache-Control "public, max-age=2592000";
        }
        
        # 不缓存 HTML 文件
        location ~* \.html$ {
            expires -1;
            add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate";
        }
    }
    
    # 限制文件上传大小
    client_max_body_size 50M;
    
    # 日志配置
    access_log /home/work/logs/dongman.access.log;
    error_log /home/work/logs/dongman.error.log;
}
```

### 3. 启用站点配置

```bash
# 验证配置是否正确
sudo nginx -t

# 如果配置正确，重新加载 Nginx
sudo systemctl reload nginx
```

## 六、SSL 证书配置

使用 Let's Encrypt 获取免费 SSL 证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d dm.xueximeng.com

# 配置自动续期
sudo systemctl status certbot.timer
```

## 七、权限配置

确保文件权限正确：

```bash
# 设置资源目录权限
sudo chmod 755 -R /home/work/dongman/
```

## 八、防火墙配置

```bash
# 允许 HTTP 和 HTTPS 流量
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 九、配置检查和测试

### 1. 检查 Supervisor 状态

```bash
sudo supervisorctl status dm
```

### 2. 检查 Nginx 状态

```bash
sudo systemctl status nginx
```
