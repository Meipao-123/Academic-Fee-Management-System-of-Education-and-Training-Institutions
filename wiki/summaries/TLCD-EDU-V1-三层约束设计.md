# TLCD-EDU-V1: 三层约束设计

**项目**: 培训机构教务收费管理系统 (EDU)
**TLCD 编号**: TLCD-EDU-V1
**版本**: V1
**日期**: 2026-06-24
**编制人**: A5-需求验证智能体
**关联文档**: ASD-EDU-V1 / SRS-v1.2 / MDS-EDU-V1 / DTS-EDU-V1 / ADR-001~004

---

## 1. 约束总览

| 层级 | 编号前缀 | 数量 | 违规阻断级别 |
|---|---|---|---|
| **架构层** (Architecture) | `C-ARCH-` | 9 条 | Blocker（违反则阻断 CI） |
| **模块层** (Module) | `C-MOD-` | 7 条 | Major（违反则警告 + PR 需审批） |
| **代码层** (Code) | `C-CODE-` | 8 条 | Major/Minor（违反则 PR 需审批） |

---

## 2. 架构层约束 (C-ARCH)

| 编号 | 约束 | 来源 | 级别 |
|---|---|---|---|
| C-ARCH-0001 | **部署拓扑**：系统必须部署为 Nginx 反向代理 + Spring Boot 模块化单体 + MySQL 主从 + Redis Sentinel。禁止拆分微服务或引入额外中间件 | ADR-001 §2 维度1, ASD §1.2 | Blocker |
| C-ARCH-0002 | **全站 HTTPS**：所有客户端→Nginx→Spring Boot 通信强制 HTTPS，HSTS 头。支付回调端点双向证书验证 | ASD §5, SRS §3.4.2 NFR-SEC-004 | Blocker |
| C-ARCH-0003 | **四层分层不可逾越**：Controller→Service→Repository→Model 严格单向。禁止 Controller 直接调用 Repository、禁止 Service 拼接 SQL、禁止跨层注入 | ASD §3.1, ASD §3.2 C-ARCH-01~03 | Blocker |
| C-ARCH-0004 | **数据隔离强制注入**：所有数据库查询必须在 WHERE 子句中包含 `campus_id`，通过 `@RequireCampus` AOP 或 Repository 基类自动注入。任何遗漏视为安全漏洞 | ASD §5, SRS §3.1.6 FR-ADM-001, MDS MOD-006 | Blocker |
| C-ARCH-0005 | **敏感数据加密与脱敏**：学员姓名/手机号/身份证号存储层 AES-256 加密（`@Encrypted`），JSON 序列化时自动脱敏（`@Masked`）。禁止明文日志输出敏感字段 | ASD §5, SRS §3.4.2 NFR-SEC-001 | Blocker |
| C-ARCH-0006 | **全链路操作日志不可变**：所有关键操作（退费/调价/权限变更/配置修改/数据修正）通过 `@Auditable` AOP 记录操作前后快照。日志写入后不可修改、不可删除 | ASD §5, SRS §3.4.5 NFR-AUD-002, MDS MOD-006 | Blocker |
| C-ARCH-0007 | **核心业务数据仅软删除**：学员/订单/财务记录删除操作设置为 `deleted=true`，禁止 `DELETE FROM`。操作日志不可删除，仅可归档 | ASD §3.2 C-ARCH-08, SRS §3.4.5 NFR-AUD-003 | Blocker |
| C-ARCH-0008 | **可用性与灾备基线**：核心业务（报名/排课/消课/财务对账）可用性 ≥99.5%。数据库全量备份每日、增量备份每 4h、异地存储。RPO≈5min, RTO≈4h | SRS §3.4.1 NFR-AVL-001/002, ADR-001 §2 维度1 | Blocker |
| C-ARCH-0009 | **外部通信降级**：短信网关不可用时自动降级为小程序推送；支付网关超时后切换异步轮询模式（每 10min 轮询 × 2h）。降级不影响核心业务流程 | ASD §4.2, SRS §3.4.3 NFR-AVL-003 [TBD], ADR-001 | Major |

---

## 3. 模块层约束 (C-MOD)

| 编号 | 约束 | 来源 | 级别 |
|---|---|---|---|
| C-MOD-0001 | **依赖方向不可逆**：严格遵循 DTS 拓扑——CORE→CRM/ACA/ADM→ENR→FIN→RPT。禁止下游模块依赖上游模块（如 FIN 不可依赖 RPT，ENR 不可依赖 FIN）。ArchUnit 自动检测，违规阻断 CI | DTS-EDU-V1 §3, ASD §2.2 | Blocker |
| C-MOD-0002 | **跨模块调用仅通过 Service 接口**：模块间调用必须依赖目标模块的 `interface`（如 `StudentService`），禁止直接注入 `impl` 或跨模块访问 Repository。返回值必须为 DTO，禁止返回 Entity | ADR-002 决策5, MDS §3 | Major |
| C-MOD-0003 | **报表模块只读**：`edu.report` 所有操作均为 SELECT，禁止 INSERT/UPDATE/DELETE。跨模块查询通过 MyBatis XML，禁止在 Service 中拼接 SQL | ASD §2.2, MDS MOD-005 | Blocker |
| C-MOD-0004 | **Core 模块零业务依赖**：`edu.core` 不依赖任何业务模块（CRM/ENR/ACA/FIN/RPT/ADM），仅包含工具类/基类/注解/异常/安全过滤器。违反此规则视为架构腐化 | DTS-EDU-V1 §3, MDS MOD-007 | Blocker |
| C-MOD-0005 | **模块内标准包结构**：每个模块必须包含 `controller/` / `service/impl/` / `repository/` / `model/{entity,dto,vo,enums}/` / `event/` / `config/`。不允许在根包直接添加类 | ASD §2.3, MDS §2 | Major |
| C-MOD-0006 | **通知/审计异步解耦**：短信发送、推送通知、审计日志写入必须通过 Spring Event + `@Async`，不得在业务 Service 中同步调用。异步失败不影响主事务 | ASD §3.2 C-ARCH-06, ASD §5, ADR-001 | Major |
| C-MOD-0007 | **模块间通信禁止直接 SQL**：跨模块数据访问通过对方模块的 Service 接口或只读视图，禁止在 A 模块的 Repository 中查询 B 模块的表 | DTS-EDU-V1 §5, MDS §4 | Major |

---

## 4. 代码层约束 (C-CODE)

| 编号 | 约束 | 来源 | 级别 |
|---|---|---|---|
| C-CODE-0001 | **统一响应体**：所有 Controller 方法必须返回 `ApiResponse<T>`（`{code, message, data, timestamp, traceId}`）。禁止直接返回裸对象或 `ResponseEntity` 手动构造 | ADR-002 决策3, ASD §4.3 | Blocker |
| C-CODE-0002 | **异常统一处理**：业务异常统一抛出 `BusinessException(errorCode, message)`，由 `@ControllerAdvice` 全局捕获并封装为 `ApiResponse`。禁止在 Controller 中 try-catch 后手动构造错误响应 | ASD §6, ADR-002 决策4 | Major |
| C-CODE-0003 | **错误码规范**：使用 6 位数字错误码 `{模块2位}{类别2位}{序号2位}`，定义在 `core.exception.ErrorCode` 枚举类中。禁止硬编码错误码字符串 | ADR-002 决策4 | Major |
| C-CODE-0004 | **缓存统一入口**：所有缓存操作通过 `core.cache.CacheService` 统一接口，禁止直接使用 `RedisTemplate` 或 `@Cacheable`。TTL 必须显式设定（最大 ≤7 天），禁止永不过期 | ADR-004 §4 | Major |
| C-CODE-0005 | **事务边界在 Service 层**：`@Transactional` 注解仅放在 Service 层 public 方法上。Repository 层不开启事务。禁止在 Controller 中开启事务 | ASD §3.1 | Major |
| C-CODE-0006 | **日志规范**：使用 Lombok `@Slf4j`。Controller 层 INFO（请求入参/出参/耗时）、Service 层 DEBUG（业务关键节点）、异常 ERROR（含 stacktrace）。禁止 `System.out.println`，禁止日志中输出明文敏感信息 | 项目编码规范 | Minor |
| C-CODE-0007 | **命名规范**：Java 类 PascalCase、方法 camelCase、常量 UPPER_SNAKE_CASE。数据库表明 `t_{模块}_{实体}`（如 `t_crm_student`）、字段名 snake_case。禁止拼音命名、禁止无意义缩写 | 项目编码规范 | Minor |
| C-CODE-0008 | **测试覆盖率**：Service 层单元测试覆盖率 ≥70%（JUnit5 + Mockito），Repository 层数据访问测试覆盖率 ≥50%（@DataJpaTest + H2）。Controller 层集成测试覆盖核心 API（@SpringBootTest + MockMvc） | 项目编码规范 | Minor |

---

## 5. 约束违反处理流程

```
CI 扫描（ArchUnit + Checkstyle + JaCoCo）
    │
    ├── Blocker 违规 → 阻断合并，必须修复才能合入 main
    │
    ├── Major 违规 → PR 标记 ⚠️，需要 Reviewer 审批后方可合入
    │
    └── Minor 违规 → PR 标记 ℹ️，建议修复但不阻断
```

---

## 6. 约束溯源矩阵

| 约束编号 | 关联 SRS | 关联 ASD | 关联 ADR | 关联 MDS/DTS |
|---|---|---|---|---|
| C-ARCH-0001 | — | §1.2 | ADR-001 维度1 | — |
| C-ARCH-0002 | NFR-SEC-004 | §5 | — | — |
| C-ARCH-0003 | — | §3.1, §3.2 | — | — |
| C-ARCH-0004 | FR-ADM-001 | §5 | — | MDS MOD-006 |
| C-ARCH-0005 | NFR-SEC-001 | §5 | — | — |
| C-ARCH-0006 | NFR-AUD-002 | §5 | — | MDS MOD-006 |
| C-ARCH-0007 | NFR-AUD-003 | §3.2 C-ARCH-08 | — | — |
| C-ARCH-0008 | NFR-AVL-001/002 | — | ADR-001 维度1 | — |
| C-ARCH-0009 | NFR-AVL-003 | §4.2 | ADR-001 | — |
| C-MOD-0001 | — | §2.2 | — | DTS §3 |
| C-MOD-0002 | — | — | ADR-002 决策5 | MDS §3 |
| C-MOD-0003 | — | §2.2 | — | MDS MOD-005 |
| C-MOD-0004 | — | — | — | DTS §3, MDS MOD-007 |
| C-MOD-0005 | — | §2.3 | — | MDS §2 |
| C-MOD-0006 | — | §3.2 C-ARCH-06 | ADR-001 | — |
| C-MOD-0007 | — | — | — | DTS §5, MDS §4 |
| C-CODE-0001 | — | §4.3 | ADR-002 决策3 | — |
| C-CODE-0002 | — | §6 | ADR-002 决策4 | — |
| C-CODE-0003 | — | — | ADR-002 决策4 | — |
| C-CODE-0004 | — | — | ADR-004 §4 | — |
| C-CODE-0005 | — | §3.1 | — | — |
| C-CODE-0006 | — | — | — | — |
| C-CODE-0007 | — | — | — | — |
| C-CODE-0008 | — | — | — | — |

---

*本 TLCD 基于 ASD / SRS / ADR-001~004 / MDS / DTS 综合提取，属于期末考核 D13 第 1 项交付物。共 24 条约束（架构 9 + 模块 7 + 代码 8）。*
