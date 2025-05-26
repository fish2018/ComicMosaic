# 数据库迁移指南

本项目使用Alembic管理数据库迁移。Alembic是一个基于SQLAlchemy的轻量级数据库迁移工具，它可以帮助我们跟踪数据库模式的变更。

## 目录结构

```
migrations/
├── alembic.ini         # Alembic配置文件
├── env.py              # 环境配置，连接数据库和加载模型
├── README.md           # 本文档
├── script.py.mako      # 迁移脚本模板
└── versions/           # 迁移脚本版本目录
    └── add_likes_count_to_resources.py  # 示例迁移脚本
```

## 基本命令

### 初始化Alembic（已完成）

```bash
# 已完成，不需要再执行
alembic init migrations
```

### 创建迁移脚本

当需要修改数据库模式时，首先在`backend/app/models/models.py`文件中更新模型定义，然后运行以下命令自动生成迁移脚本：

```bash
# 自动根据模型变更生成迁移脚本
alembic -c migrations/alembic.ini revision --autogenerate -m "描述你的变更"
```

例如：

```bash
alembic -c migrations/alembic.ini revision --autogenerate -m "add email column to users"
```

### 手动创建迁移脚本

如果你需要手动编写迁移脚本，可以使用以下命令：

```bash
alembic -c migrations/alembic.ini revision -m "描述你的变更"
```

然后编辑生成的脚本文件，在`upgrade()`和`downgrade()`函数中分别添加向上和向下迁移的SQL操作。

### 应用迁移

```bash
# 应用所有未应用的迁移
alembic -c migrations/alembic.ini upgrade head

# 应用特定版本的迁移
alembic -c migrations/alembic.ini upgrade <revision_id>

# 升级指定步数
alembic -c migrations/alembic.ini upgrade +1
```

### 回滚迁移

```bash
# 回滚到上一个版本
alembic -c migrations/alembic.ini downgrade -1

# 回滚到特定版本
alembic -c migrations/alembic.ini downgrade <revision_id>

# 回滚所有迁移
alembic -c migrations/alembic.ini downgrade base
```

### 查看迁移历史

```bash
# 查看迁移历史
alembic -c migrations/alembic.ini history

# 查看当前版本
alembic -c migrations/alembic.ini current
```

## 迁移流程示例

1. 在models.py文件中添加新列或修改现有模型
2. 生成迁移脚本：`alembic -c migrations/alembic.ini revision --autogenerate -m "添加XXX字段"`
3. 检查生成的迁移脚本是否符合预期（位于`migrations/versions/`目录下）
4. 应用迁移：`alembic -c migrations/alembic.ini upgrade head`
5. 验证数据库中的变更是否生效

## 注意事项

1. 在生产环境应用迁移前，务必在测试环境验证迁移脚本
2. 经常备份数据库，尤其是在执行迁移前
3. Alembic不能检测所有类型的模式变更，有时需要手动编辑生成的迁移脚本
4. 确保迁移脚本中包含适当的回滚操作（downgrade函数）

## 常见问题排查

1. **模型变更没有被检测到**：确保在模型中正确导入了Base类，并且表类继承自Base
2. **迁移脚本执行失败**：检查数据库是否有与迁移冲突的约束或数据
3. **找不到表或列**：确认表名和列名在模型中拼写正确 