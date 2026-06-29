# ASD-EDU-V1: 架构风格声明

**项目**: 培训机构教务收费管理系统 (EDU)
**ASD 编号**: ASD-EDU-V1
**版本**: V1
**日期**: 2026-06-24
**编制人**: A5-需求验证智能体（全量执行角色）
**关联文档**: SRS-v1.2 / ADR-001 / UML 用例图-v1.0

---

## 1. 架构风格概述

### 1.1 风格声明

本系统采用 **模块化分层单体架构（Modular Layered Monolith）**，以 **Controller-Service-Repository-Model 四层分层** 为核心结构模式，辅以 **RESTful 资源导向** 的对外接口风格。

```
                     ┌──────────────────────────┐
                     │        Nginx :443         │ ← HTTPS 反向代理
                     └──────────┬───────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │PC Web 端  │    │小程序端   │    │第三方回调 │
        │(Admin SPA)│    │(家长端)   │    │(微信/支付宝)│
        └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
              │               │               │
              └───────────────┼───────────────┘
                              │ RESTful JSON / HTTPS
              ┌───────────────┴───────────────┐
              │       Spring Boot 应用         │
              │  ┌─────────────────────────┐  │
              │  │     Controller 层       │  │  ← @RestController
              │  │  参数校验 / 响应封装     │  │     @Validated
              │  ├─────────────────────────┤  │
              │  │      Service 层         │  │  ← @Service
              │  │  业务编排 / 事务 / 权限  │  │     @Transactional
              │  ├─────────────────────────┤  │
              │  │    Repository 层        │  │  ← @Repository
              │  │  JPA + MyBatis + Redis  │  │     Row-Level Security
              │  ├─────────────────────────┤  │
              │  │      Model 层           │  │  ← Entity/DTO/VO/Enum
              │  │  纯数据结构              │  │
              │  └─────────────────────────┘  │
              │  ┌─────────────────────────┐  │
              │  │  横切关注点 (AOP)        │  │
              │  │  @Auditable 审计日志     │  │
              │  │  @RequireCampus 数据隔离  │  │
              │  │  @RateLimit 接口限流     │  │
              │  └─────────────────────────┘  │
              └───────────┬───────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   ┌─────────┐     ┌─────────┐      ┌──────────┐
   │  MySQL  │     │  Redis  │      │ 外部 API  │
   │ 主从+异地│     │ Sentinel│      │支付/短信等│
   └─────────┘     └─────────┘      └──────────┘
```

### 1.2 风格选择理由

| 维度 | 选择 | 理由 |
|---|---|---|
| **系统规模** | 单体 > 微服务 | 29 FR，5 类涉众，单人团队，微服务运维 overhead 远超收益 |
| **模块化** | 6 功能模块 + 共用 core 模块 | 按 SRS 的 CRM/ENR/ACA/FIN/RPT/ADM 分包，边界清晰 |
| **分层** | 严格四层 | Controller→Service→Repository→Model，禁止跨层调用 |
| **通信** | 同步 RESTful + 异步 Spring Event | 核心交易同步、通知/审计异步 |
| **数据** | 单库 + Row-Level Security | 应用层 `campus_id` 注入，兼顾查询性能与多校区隔离 |

---

## 2. 模块划分与边界

### 2.1 功能模块

```
edu.crm          ← 线索与学员管理      (FR-CRM-001~005)
edu.enrollment   ← 报名缴费与订单管理   (FR-ENR-001~005)
edu.academic     ← 教务排课与消课管理   (FR-ACA-001~005)
edu.finance      ← 财务管理与核算       (FR-FIN-001~004)
edu.report       ← 报表分析与决策驾驶舱 (FR-RPT-001~005)
edu.admin        ← 系统管理与基础配置   (FR-ADM-001~005)
edu.core         ← 共用基础设施
```

### 2.2 模块间依赖规则

```
                    ┌──────────┐
                    │ edu.core │  ← 被所有模块依赖（无反向依赖）
                    └────┬─────┘
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
     ┌──────────┐ ┌──────────┐ ┌──────────┐
     │ edu.crm  │ │edu.academic│ │edu.admin │
     └────┬─────┘ └────┬─────┘ └────┬─────┘
          │            │            │
          ▼            ▼            ▼
     ┌──────────┐ ┌──────────┐ ┌──────────┐
     │edu.enrollment│ │edu.finance│ │edu.report│
     └─────────────┘ └──────────┘ └──────────┘
```

**依赖约束**:
- `edu.core`: 零依赖（不依赖任何业务模块）
- `edu.crm / edu.academic / edu.admin`: 仅依赖 `edu.core`
- `edu.enrollment`: 依赖 `edu.core` + `edu.crm`（报名需要学员信息）
- `edu.finance`: 依赖 `edu.core` + `edu.enrollment`（财务依赖订单数据）
- `edu.report`: 依赖 `edu.core` + `edu.enrollment` + `edu.finance` + `edu.academic`（报表跨模块读取）
- **严禁**: 下游模块直接调用上游模块的 Service（如 `edu.finance` 不能调用 `edu.report`）

### 2.3 模块内标准包结构

```
com.meipao.edu.{module}
├── controller/     # REST Controller
├── service/        # 业务逻辑接口 + 实现
│   └── impl/
├── repository/     # JPA Repository + MyBatis Mapper
├── model/
│   ├── entity/     # JPA Entity
│   ├── dto/        # 请求/响应 DTO
│   ├── vo/         # 视图 VO (报表用)
│   └── enums/      # 枚举
├── event/          # Spring Event (领域事件)
└── config/         # 模块级配置
```

---

## 3. 四层分层约束

### 3.1 调用规则

```
Controller ──→ Service ──→ Repository ──→ Model
   │              │
   ├── 可调用 Service
   ├── 可直接使用 Model (DTO/VO)
   ├── 禁止调用 Repository（绕过 Service）
   └── 禁止包含业务逻辑
   
Service
   ├── 可调用 Repository
   ├── 可调用其他模块的 Service（通过接口，非实现）
   ├── 不含 SQL（SQL 在 Repository 中）
   └── 事务边界（@Transactional 在 Service 层）

Repository
   ├── JPA: 接口继承 JpaRepository
   ├── MyBatis: Mapper 接口 + XML
   ├── 不含业务逻辑
   └── 基类自动注入 campus_id WHERE 条件

Model
   ├── Entity: JPA 映射
   ├── DTO: 请求/响应体
   ├── VO: MyBatis 查询结果映射
   └── Enum: 订单状态/收款状态/调课状态等（对应 SRS §3.3.2）
```

### 3.2 禁止模式（C-ARCH 负面约束）

| 编号 | 禁止模式 | 说明 |
|---|---|---|
| C-ARCH-01 | Controller 中写业务逻辑 | Controller 仅做参数校验、调用 Service、封装响应 |
| C-ARCH-02 | Service 中拼接 SQL | SQL 全部在 Repository（JPA 方法命名 / MyBatis XML）|
| C-ARCH-03 | 跨层绕过 | Controller 不可直接调用 Repository |
| C-ARCH-04 | 模块间循环依赖 | 严格遵守 §2.2 依赖拓扑（DTS 中正式声明） |
| C-ARCH-05 | 硬编码配置 | 所有配置项通过 `application.yml` 或系统配置表（FR-ADM-004）管理 |
| C-ARCH-06 | Service 中发送短信/推送 | 短信/推送通过 Spring Event 异步解耦，不可在业务 Service 中同步调用 |
| C-ARCH-07 | 忽略 campus_id 过滤 | 所有数据访问必须通过 `campus_id` 过滤（基类强制注入 + AOP 校验） |
| C-ARCH-08 | 物理删除核心数据 | 学员/订单/财务记录仅软删除（NFR-AUD-003），操作日志不可删除（NFR-AUD-002） |

---

## 4. 通信与集成约束

### 4.1 内部通信

| 通信类型 | 方式 | 用途 | 约束 |
|---|---|---|---|
| **同步调用** | 方法调用（同一模块）/ RESTful API（跨模块） | 核心业务流程 | 跨模块调用仅通过 Service 接口 |
| **异步事件** | Spring Event + @Async | 审计日志写入、短信发送、推送通知 | 发送失败不影响主流程 |
| **缓存** | Redis | Session、支付幂等令牌、排课冲突检测 | 缓存失效不影响业务正确性 |

### 4.2 外部集成

| 外部系统 | 协议 | 超时 | 重试 | 降级 |
|---|---|---|---|---|
| 微信支付 | HTTPS + 证书 | 15s | 异步轮询，10min×12次 | 标记待补录 |
| 支付宝 | HTTPS + 证书 | 15s | 同上 | 标记待补录 |
| 短信网关 | HTTPS | 5s | 3次（间隔递增） | 降级为小程序推送 |
| 小程序推送 | HTTPS | 5s | 3次 | 静默失败 |

### 4.3 API 设计约定

| 约定 | 规范 |
|---|---|
| **URL 风格** | RESTful 资源导向：`/api/v1/{module}/{resource}/{id}` |
| **请求/响应格式** | JSON，统一响应体 `{ code, message, data }` |
| **分页** | `GET /api/v1/{resource}?page=0&size=20&sort=createdAt,desc` |
| **错误码** | 6 位数字：`{模块2位}{类别2位}{序号2位}`（如 010101=CRM模块-参数校验-手机号格式错误） |
| **版本控制** | URL 前缀版本号 `/api/v1/`，大版本升级平滑过渡 |
| **文档** | Springdoc OpenAPI 自动生成，`/swagger-ui.html` |

---

## 5. 安全约束

| 层次 | 约束 |
|---|---|
| **传输** | 全站 HTTPS，HSTS 头 |
| **认证** | 管理端：JWT（Access Token 2h + Refresh Token 7d）；小程序端：微信 OAuth |
| **授权** | `@PreAuthorize("hasRole('FINANCE')")` 方法级注解 |
| **数据范围** | `@RequireCampus` 自定义注解 + AOP 自动注入 `campus_id` 过滤 |
| **支付** | 回调验签 + 幂等令牌（Redis 10min TTL） |
| **敏感字段** | `@Encrypted` 注解触发 AES-256 加解密 |
| **脱敏** | `@Masked` 注解触发 Jackson 序列化时自动脱敏 |
| **审计** | `@Auditable(action, module)` 注解，AOP 记录操作前后快照 |

---

## 6. 错误处理约束

| 层级 | 约束 |
|---|---|
| **Controller** | `@ControllerAdvice` 全局异常处理，统一返回 `{ code, message, data }` |
| **Service** | 业务异常抛出 `BusinessException(code, message)`，不吞异常 |
| **Repository** | 数据访问异常转换为 `DataAccessException` 子类 |
| **外部调用** | 超时/网络异常 → 重试策略 → 超过阈值 → 降级处理 + 告警 |

---

## 7. 与 UML 模型的映射

| UML 图 | 对应模块 | 关键约束来源 |
|---|---|---|
| 用例图 (35 用例) | 全部 6 模块 | Controller 方法粒度对齐用例 |
| 报名缴费活动图 | `edu.enrollment` + `edu.finance` | 支付→对账流程在 Service 层编排 |
| 退费流程活动图 | `edu.finance` + `edu.admin` | 多级审批在 Service 层实现 |
| 排课消课活动图 | `edu.academic` | 调课协同闭环含定时任务（超时释放） |

---

## 8. 演进预留

| 当前设计 | 未来演进方向 | 触发条件 |
|---|---|---|
| 模块化单体 | 微服务拆分（按 6 模块） | 某模块需要独立部署/扩展/技术栈异构 |
| Spring Event | RabbitMQ / Kafka | 异步事件量超过单机处理能力 |
| 单 MySQL 主从 | 读写分离 + 分库 | 数据量 > 500GB 或读 QPS > 1000 |
| 应用层 campus_id 过滤 | 独立数仓副本（TBD-15） | 集团统计分析需求复杂化 |

---

*本 ASD 随 ADR-001 一同产出，属于期末考核第 1 项交付物（ADR-001 + ASD）。版本 V1，后续经 CCB 审批后正式冻结。*
