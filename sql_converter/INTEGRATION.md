# SQL转换器模块集成说明

## 功能说明

本模块实现将Excel文件中包含 `wm_concat` 函数的Oracle SQL语句转换为 `listagg` 函数。

- **wm_concat**: Oracle 10g/11g 中的自定义聚合函数
- **listagg**: Oracle 12c+ 中的标准聚合函数

## 转换规则

```sql
-- 转换前
SELECT wm_concat(column_name) FROM table_name

-- 转换后
SELECT listagg(column_name, ',') within group (order by column_name) FROM table_name
```

## 集成步骤

### 1. 复制文件

将 `sql_converter` 文件夹复制到你的Django项目根目录下。

### 2. 注册应用

在 `yp_djangoProject/settings.py` 中的 `INSTALLED_APPS` 添加：

```python
INSTALLED_APPS = [
    # ... 其他应用
    'excel_app',
    'zip_app',
    'sql_converter',  # 添加这一行
]
```

### 3. 配置媒体文件（如未配置）

确保 `yp_djangoProject/settings.py` 中有以下配置：

```python
import os

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 4. 添加URL路由

在 `yp_djangoProject/urls.py` 中添加：

```python
urlpatterns = [
    # ... 其他路由
    path('excel/', include('excel_app.urls')),
    path('zip/', include('zip_app.urls')),
    path('sql-converter/', include('sql_converter.urls')),  # 添加这一行
    path('', views.index, name='index'),
]
```

### 5. 执行数据库迁移

```bash
python manage.py makemigrations sql_converter
python manage.py migrate
```

### 6. 创建上传目录

```bash
mkdir -p media/sql_converter_files
```

## 使用方法

1. 启动Django开发服务器：
   ```bash
   python manage.py runserver
   ```

2. 访问转换器页面：
   ```
   http://localhost:8000/sql-converter/upload/
   ```

3. 上传包含 `RULE_SQL_VALUE` 列的Excel文件

4. 系统自动转换并生成下载链接

## 文件结构

```
sql_converter/
├── __init__.py
├── admin.py          # 后台管理配置
├── apps.py           # 应用配置
├── forms.py          # 表单定义
├── models.py         # 数据模型
├── sql_parser.py     # SQL转换核心逻辑
├── urls.py           # URL路由
├── views.py          # 视图函数
├── templates/        # 模板文件
│   ├── upload_sql_converter.html
│   └── sql_converter_preview.html
└── INTEGRATION.md    # 本说明文件
```

## Excel文件要求

- 文件格式：`.xlsx` 或 `.xls`
- 必须包含列：`RULE_SQL_VALUE`
- 转换结果将保存在新列：`RULE_SQL_VALUE_CONVERTED`

## 支持的转换模式

- `wm_concat(column)` → `listagg(column, ',') within group (order by column)`
- `wm_concat(distinct column)` → `listagg(distinct column, ',') within group (order by column)`
- `wm_concat(unique column)` → `listagg(unique column, ',') within group (order by column)`
- 支持嵌套的wm_concat函数

## 注意事项

1. 转换后的SQL语句保存在新列中，不会覆盖原始数据
2. 如果SQL中没有wm_concat函数，则转换后列与原始列内容相同
3. 支持批量处理多个包含wm_concat的SQL语句
