# SoLove Backend - Python 开发指南

> 专为 Java 开发者转型 Python 编写  
> 版本：V1.0  
> 日期：2026 年 4 月 11 日

---

## 一、快速对比：Java vs Python (FastAPI)

作为 Java 开发者，这些概念你会很熟悉：

| Java 概念 | Python (FastAPI) 对应 | 说明 |
|-----------|---------------------|------|
| **Spring Boot** | FastAPI | Web 框架 |
| **Main 方法** | `uvicorn app.main:app` | 启动入口 |
| **@RestController** | `@router.get/post/put/delete` | 路由装饰器 |
| **@Service** | `services/` 模块 | 业务逻辑层 |
| **@Repository** | `models/` + SQLAlchemy | 数据访问层 |
| **DTO/VO** | `schemas/` (Pydantic) | 数据传输对象 |
| **Entity** | `models/` (SQLAlchemy) | 实体类 |
| **application.yml** | `.env` + `config.py` | 配置文件 |
| **Maven/Gradle** | `pip` + `requirements.txt` | 依赖管理 |
| **Tomcat/Jetty** | Uvicorn | 应用服务器 |

---

## 二、项目架构

### 2.1 整体结构

```
solove_backend/
├── app/                          # 应用主目录 (相当于 src/main/java)
│   ├── __init__.py               # Python 包标识 (类似 package-info.java)
│   ├── main.py                   # ⭐ 启动入口 (类似 SpringBootApplication)
│   │
│   ├── core/                     # 核心配置 (类似 config 包)
│   │   ├── __init__.py
│   │   ├── config.py             # 配置类 (类似 @Configuration)
│   │   └── database.py           # 数据库配置 (类似 DataSourceConfig)
│   │
│   ├── models/                   # 数据模型 (类似 entity 包)
│   │   ├── __init__.py
│   │   └── models.py             # SQLAlchemy 实体类 (类似 @Entity)
│   │
│   ├── schemas/                  # 数据模式 (类似 dto/vo 包)
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic 模型 (类似 DTO/VO)
│   │
│   ├── api/                      # API 路由 (类似 controller 包)
│   │   ├── __init__.py
│   │   ├── users.py              # 用户接口 (类似 UserController)
│   │   ├── tasks.py              # 任务接口 (类似 TaskController)
│   │   └── checkins.py           # 打卡接口 (类似 CheckinController)
│   │
│   └── services/                 # 业务逻辑 (类似 service 包)
│       ├── __init__.py
│       └── (后续添加业务逻辑)
│
├── tests/                        # 测试目录 (类似 src/test/java)
│   └── __init__.py
│
├── requirements.txt              # ⭐ 依赖清单 (类似 pom.xml)
├── .env                          # ⭐ 环境变量配置 (类似 application.yml)
├── .env.example                  # 配置模板
├── .gitignore                    # Git 忽略文件
└── README.md                     # 项目说明
```

---

## 三、启动流程

### 3.1 启动命令

```bash
# 开发环境（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**解释：**
- `app.main:app` = `模块名：变量名`
- 类似 Java 的 `com.example.demo.DemoApplication.main()`

### 3.2 启动流程图

```
┌─────────────────┐
│  执行 uvicorn   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  导入 app.main  │  ← 类似 Spring Boot 启动类
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  创建 FastAPI   │  ← 类似 new SpringApplication()
│  应用实例       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  创建数据库表   │  ← 类似 Flyway/Liquibase
│  Base.metadata  │
│  .create_all()  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  注册路由       │  ← 类似 @RestController 扫描
│  app.include_   │
│  router()       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  启动 Uvicorn   │  ← 类似 Tomcat 启动
│  服务器         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  监听 8000 端口  │  ← 服务就绪
└─────────────────┘
```

---

## 四、核心文件详解

### 4.1 🚀 启动入口：`app/main.py`

```python
"""
SoLove Backend - 主应用入口

寓意：Solo + Love = So Love
独自爱自己，也是一种爱
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import Base, engine
from .api import users, tasks, checkins

# 创建数据库表 (类似 Flyway 迁移)
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用 (类似 new SpringApplicationBuilder())
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS (类似 WebMvcConfigurer)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["根路径"])
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": "/docs"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "solove-backend"}


# 注册路由 (类似 @ComponentScan 扫描 Controller)
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(checkins.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
```

**Java 对比：**
```java
// 这相当于你的 Spring Boot 启动类
@SpringBootApplication
public class SoloveApplication {
    public static void main(String[] args) {
        SpringApplication.run(SoloveApplication.class, args);
    }
}
```

---

### 4.2 ⚙️ 配置管理：`app/core/config.py`

```python
"""
应用核心配置

类似 Java 的 @Configuration + @Value
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "SoLove Backend"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "情绪陪伴打卡 APP 后端服务"
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/solove"
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天
    
    # AI 配置
    AI_API_KEY: Optional[str] = None
    AI_API_BASE: Optional[str] = None
    AI_MODEL: str = "qwen-plus"
    
    class Config:
        env_file = ".env"  # 从 .env 文件读取配置
        case_sensitive = True


# 全局配置实例 (类似 Spring 的 @Autowired Settings)
settings = Settings()
```

**.env 文件（类似 application.yml）：**
```bash
# 应用配置
APP_NAME=SoLove Backend
APP_VERSION=0.1.0
DEBUG=True

# 数据库配置
DATABASE_URL=postgresql://solove:solove_password@localhost:5432/solove

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# JWT 配置
SECRET_KEY=solove-secret-key-2026-change-in-production
```

---

### 4.3 🗄️ 数据库配置：`app/core/database.py`

```python
"""
数据库配置

类似 Java 的 DataSourceConfig + EntityManagerFactory
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# 创建数据库引擎 (类似 DriverManagerDataSource)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 打印 SQL 日志 (类似 logging)
    pool_pre_ping=True,   # 连接前检查
    pool_size=10,         # 连接池大小
    max_overflow=20       # 最大溢出连接数
)

# 创建会话工厂 (类似 EntityManagerFactory)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类 (类似 @MappedSuperclass)
Base = declarative_base()


def get_db():
    """
    获取数据库会话（依赖注入用）
    
    类似 Spring 的 @Autowired EntityManager
    但这里是函数式依赖注入
    """
    db = SessionLocal()
    try:
        yield db  # yield 表示这是一个生成器
    finally:
        db.close()  # 确保关闭连接
```

---

### 4.4 📊 数据模型：`app/models/models.py`

```python
"""
数据库模型定义

类似 Java 的 @Entity 实体类
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class User(Base):
    """用户表 - 类似 JPA Entity"""
    __tablename__ = "users"  # 表名
    
    id = Column(Integer, primary_key=True, index=True)  # 主键
    openid = Column(String(64), unique=True, index=True, comment="用户唯一标识")
    nickname = Column(String(64), comment="昵称")
    avatar_url = Column(String(255), comment="头像 URL")
    
    # 情绪相关
    mood_baseline = Column(Float, default=5.0, comment="基础情绪分值 (1-10)")
    preferences = Column(Text, comment="用户偏好 (JSON)")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_premium = Column(Boolean, default=False, comment="是否付费会员")
    
    # 时间 (类似 @CreatedDate @LastModifiedDate)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系 (类似 @OneToMany)
    tasks = relationship("UserTask", back_populates="user", cascade="all, delete-orphan")
    checkins = relationship("Checkin", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
```

**Java 对比：**
```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true)
    private String openid;
    
    private String nickname;
    
    // ... 其他字段
    
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL)
    private List<UserTask> tasks;
}
```

---

### 4.5 📦 数据模式：`app/schemas/schemas.py`

```python
"""
Pydantic Schemas - API 请求/响应模型

类似 Java 的 DTO/VO 类
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ 用户相关 ============

class UserBase(BaseModel):
    """用户基础模型 - 类似 DTO 基类"""
    nickname: Optional[str] = Field(None, max_length=64)
    avatar_url: Optional[str] = None
    mood_baseline: Optional[float] = Field(5.0, ge=1, le=10)


class UserCreate(UserBase):
    """用户创建 - 类似 CreateRequest DTO"""
    openid: str = Field(..., max_length=64)  # ... 表示必填


class UserUpdate(BaseModel):
    """用户更新 - 类似 UpdateRequest DTO"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    mood_baseline: Optional[float] = Field(None, ge=1, le=10)
    preferences: Optional[dict] = None


class UserResponse(UserBase):
    """用户响应 - 类似 Response VO"""
    id: int
    openid: str
    is_active: bool
    is_premium: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # 允许从 ORM 对象读取 (类似 BeanUtils)
```

**Pydantic 的优势：**
- ✅ 自动验证（类似 Hibernate Validator）
- ✅ 自动类型转换
- ✅ 自动生成 OpenAPI 文档

---

### 4.6 🎯 API 路由：`app/api/users.py`

```python
"""
用户相关 API

类似 Java 的 @RestController
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..models.models import User
from ..schemas.schemas import UserCreate, UserResponse, UserUpdate, DataResponse

# 创建路由 (类似 @RestController)
router = APIRouter(prefix="/api/users", tags=["用户"])


@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    
    - **openid**: 用户唯一标识（微信/小程序等）
    - **nickname**: 昵称（可选）
    - **mood_baseline**: 基础情绪分 1-10（可选，默认 5）
    """
    # 检查用户是否已存在 (类似 userRepository.findByOpenid())
    existing_user = db.query(User).filter(User.openid == user_data.openid).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户已存在")
    
    # 创建新用户 (类似 new User() + entityManager.persist())
    new_user = User(
        openid=user_data.openid,
        nickname=user_data.nickname,
        avatar_url=user_data.avatar_url,
        mood_baseline=user_data.mood_baseline
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user  # 自动序列化为 JSON


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user(
    openid: str,
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息
    
    - **openid**: 用户唯一标识
    """
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已禁用")
    
    return user
```

**Java 对比：**
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserRepository userRepository;
    
    @PostMapping("/register")
    public ResponseEntity<UserResponse> register(@RequestBody UserCreate user_data) {
        // 类似逻辑
    }
    
    @GetMapping("/me")
    public ResponseEntity<UserResponse> getCurrentUser(@RequestParam String openid) {
        // 类似逻辑
    }
}
```

---

## 五、Python 关键概念

### 5.1 装饰器 (Decorator)

**类似 Java 的注解 (Annotation)，但是函数式**

```python
# Python 装饰器
@router.get("/users", response_model=UserResponse)
async def get_users():
    pass

# Java 注解
@GetMapping("/users")
public ResponseEntity<UserResponse> getUsers() {
    pass
}
```

### 5.2 类型提示 (Type Hints)

**Python 3.5+ 的类型系统，类似 Java 的泛型**

```python
# Python 类型提示
def greet(name: str, age: int) -> str:
    return f"{name} is {age} years old"

# Java 类似
public String greet(String name, Integer age) {
    return name + " is " + age + " years old";
}
```

### 5.3 异步 (Async/Await)

**类似 Java 的 CompletableFuture/Reactive**

```python
# Python 异步
async def fetch_data():
    result = await httpx.get("https://api.example.com")
    return result.json()

# Java 类似
public CompletableFuture<JsonNode> fetchData() {
    return httpClient.getAsync("https://api.example.com")
        .thenApply(Response::getBody);
}
```

### 5.4 依赖注入 (Dependency Injection)

**FastAPI 使用函数式依赖注入，类似 Spring 的 @Autowired**

```python
# FastAPI 依赖注入
@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    # db 自动注入
    pass

# Spring 依赖注入
@Autowired
private EntityManager entityManager;
```

### 5.5 上下文管理器 (Context Manager)

**类似 Java 的 try-with-resources**

```python
# Python 上下文管理器
with open("file.txt", "r") as f:
    content = f.read()
# 自动关闭文件

# Java try-with-resources
try (BufferedReader f = new BufferedReader(new FileReader("file.txt"))) {
    String content = f.readLine();
}
```

---

## 六、开发流程

### 6.1 添加新功能的步骤

**以添加"删除用户"接口为例：**

#### 步骤 1：在 schemas.py 添加请求/响应模型（如需要）

```python
# app/schemas/schemas.py
class UserDeleteResponse(BaseModel):
    """用户删除响应"""
    success: bool
    message: str
    user_id: int
```

#### 步骤 2：在 api/users.py 添加路由

```python
# app/api/users.py
@router.delete("/{user_id}", response_model=UserDeleteResponse, summary="删除用户")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    
    return UserDeleteResponse(
        success=True,
        message="用户已删除",
        user_id=user_id
    )
```

#### 步骤 3：重启服务，访问文档测试

```bash
# 开发环境自动热重载
uvicorn app.main:app --reload

# 访问 API 文档
http://localhost:8000/docs
```

---

### 6.2 调试技巧

#### 打印日志

```python
# 类似 System.out.println
print(f"User ID: {user_id}")

# 类似 Logger
import logging
logging.info(f"User ID: {user_id}")
```

#### 查看 SQL 日志

在 `app/core/database.py` 中设置 `echo=True`：

```python
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # 打印所有 SQL
    ...
)
```

#### 使用断点

```python
# 类似 Java 断点
import pdb; pdb.set_trace()

# Python 3.7+
breakpoint()
```

---

## 七、常用命令

### 7.1 依赖管理

```bash
# 安装所有依赖 (类似 mvn install)
pip install -r requirements.txt

# 安装单个包
pip install fastapi

# 查看已安装的包
pip list

# 导出依赖 (类似生成 pom.xml)
pip freeze > requirements.txt
```

### 7.2 运行服务

```bash
# 开发环境（热重载）
uvicorn app.main:app --reload

# 指定端口
uvicorn app.main:app --reload --port 8080

# 生产环境
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 7.3 代码格式化

```bash
# 安装格式化工具
pip install black isort flake8

# 格式化代码
black app/

# 排序 import
isort app/

# 代码检查
flake8 app/
```

### 7.4 运行测试

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/test_users.py

# 带覆盖率
pytest --cov=app
```

---

## 八、Java vs Python 思维转换

### 8.1 从"类"到"函数"

**Java 思维：**
```java
public class UserService {
    private final UserRepository repository;
    
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
    
    public User getUser(Long id) {
        return repository.findById(id).orElseThrow();
    }
}
```

**Python 思维：**
```python
# 更简洁，直接用函数
def get_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)
    return user
```

### 8.2 从"显式"到"隐式"

**Java：** 类型、异常、依赖都要显式声明

**Python：** 更灵活，但要用好类型提示

### 8.3 从"编译时"到"运行时"

**Java：** 编译时检查，类型安全

**Python：** 运行时检查，更灵活但要写好测试

---

## 九、最佳实践

### 9.1 代码风格

- ✅ 使用类型提示（类似 Java 的泛型）
- ✅ 函数要有文档字符串（类似 Javadoc）
- ✅ 遵循 PEP 8 规范（类似 Java Code Conventions）
- ✅ 使用 Black 自动格式化

### 9.2 错误处理

```python
# 好的做法
from fastapi import HTTPException

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

# 不好的做法（不要这样）
try:
    user = db.query(User).filter(User.id == user_id).first()
    return user
except Exception as e:
    print(e)  # 不要静默吞掉异常
```

### 9.3 数据库操作

```python
# 好的做法 - 使用依赖注入
@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# 不好的做法 - 全局 Session
db = SessionLocal()  # ❌ 不要这样做

@router.get("/users")
async def get_users():
    users = db.query(User).all()
    return users
```

---

## 十、学习资源

### 10.1 官方文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/) - 非常详细，有中文
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)

### 10.2 推荐教程

- [FastAPI 中文教程](https://fastapi.tiangolo.com/zh/tutorial/)
- [Python 官方教程](https://docs.python.org/3/tutorial/)

### 10.3 工具推荐

- **IDE**: VS Code (Python 插件) 或 PyCharm
- **API 测试**: 直接用 `/docs` (Swagger UI)
- **数据库管理**: DBeaver 或 pgAdmin

---

## 十一、快速上手清单

### ✅ 环境准备

- [ ] 安装 Python 3.9+
- [ ] 安装 PostgreSQL
- [ ] 安装 Redis (可选，定时任务用)

### ✅ 项目启动

- [ ] `cd solove_backend`
- [ ] `pip install -r requirements.txt`
- [ ] 复制 `.env.example` 到 `.env` 并修改配置
- [ ] `uvicorn app.main:app --reload`
- [ ] 访问 `http://localhost:8000/docs`

### ✅ 第一个接口

- [ ] 在 `app/api/users.py` 添加一个新接口
- [ ] 重启服务（或自动热重载）
- [ ] 在 `/docs` 测试接口

### ✅ 数据库操作

- [ ] 在 `app/models/models.py` 添加一个新模型
- [ ] 在接口中使用 `db.query()` 操作数据
- [ ] 测试 CRUD 操作

---

## 十二、常见问题 FAQ

### Q1: 如何调试？

**A:** 用 `print()` 或 `breakpoint()`，或者用 IDE 的调试器。

### Q2: 如何处理异常？

**A:** 用 `try-except` 或 `raise HTTPException()`。

### Q3: 如何做事务？

**A:** `db.commit()` 提交，`db.rollback()` 回滚。

### Q4: 如何做异步？

**A:** 用 `async def` 和 `await`。

### Q5: 如何部署？

**A:** 用 Uvicorn + Gunicorn 或 Docker。

---

## 十三、总结

### Python (FastAPI) vs Java (Spring Boot)

| 维度 | Java (Spring) | Python (FastAPI) |
|------|---------------|------------------|
| **学习曲线** | 陡峭 | 平缓 |
| **开发速度** | 较慢 | 快 |
| **运行性能** | 高 | 中等 |
| **类型安全** | 强 | 中等（有类型提示） |
| **生态成熟度** | 非常成熟 | 快速成熟 |
| **适合场景** | 大型企业应用 | 快速迭代、API 服务 |

### 给 Java 开发者的建议

1. **放下"类"的执念** - Python 更偏向函数式
2. **用好类型提示** - 虽然可选，但建议用
3. **写好测试** - 运行时语言更需要测试保障
4. **享受简洁** - Python 代码量通常是 Java 的 1/3

---

> **祝你在 Python 的世界里玩得开心！** 🐍

> SoLove = Solo + Love = So Love  
> 独自爱自己，也是一种爱 ❤️
