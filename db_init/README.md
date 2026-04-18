# db_init

本目录用于存放**数据库表结构相关的 SQL**（建表、索引、外键等），便于：

- 与 `app/models/models.py` 对照审查
- 在本地或 CI 中手工执行初始化
- 作为团队约定的「表结构文档」补充（应用仍可用 SQLAlchemy `create_all` 做开发）

## 使用方式（本地 MySQL）

1. 创建数据库（库名需与 `.env` 中 `DATABASE_URL` 一致，默认 `solove`）：

```sql
CREATE DATABASE IF NOT EXISTS solove
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

2. 在已选中的库下执行建表脚本：

```bash
mysql -u你的用户 -p solove < db_init/001_schema_tables.sql
```

或在客户端中打开 `001_schema_tables.sql` 执行。

**注意**：`001_schema_tables.sql` 内含 `DROP TABLE`，会删除上述业务表及数据，**仅适合开发环境或空库初始化**；生产环境请用迁移工具或手写增量脚本。

## 与 ORM 的关系

- 表名、字段、外键尽量与 SQLAlchemy 模型一致。
- `updated_at` 在模型里由 ORM `onupdate` 维护；纯 SQL 建表未写 `ON UPDATE`，更新依赖应用写入。

## 文件约定

- `001_schema_tables.sql`：当前版本的完整建表语句（可按需拆分为 `002_*.sql` 迁移片段）。
