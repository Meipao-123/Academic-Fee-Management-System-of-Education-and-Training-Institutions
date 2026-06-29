# MDS-EDU-V1: 模块定义规范

**项目**: 培训机构教务收费管理系统 (EDU)
**MDS 编号**: MDS-EDU-V1
**版本**: V1
**日期**: 2026-06-24
**编制人**: A5-需求验证智能体（全量执行角色）
**关联文档**: ASD-EDU-V1 (§2 模块划分) / SRS-v1.2 (§3.1.1~§3.1.6 功能需求) / ADR-001

---

## 1. 模块总览

本系统按 SRS 的 6 个功能需求模块 + 1 个共用基础设施模块划分为 **7 个模块**：

| 模块 ID | 全限定包名 | 名称 | SRS 章节 | FR 覆盖 |
|---|---|---|---|---|
| MOD-001 | `com.meipao.edu.crm` | 线索与学员管理 | §3.1.1 | FR-CRM-001~005 |
| MOD-002 | `com.meipao.edu.enrollment` | 报名缴费与订单管理 | §3.1.2 | FR-ENR-001~005 |
| MOD-003 | `com.meipao.edu.academic` | 教务排课与消课管理 | §3.1.3 | FR-ACA-001~005 |
| MOD-004 | `com.meipao.edu.finance` | 财务管理与核算 | §3.1.4 | FR-FIN-001~004 |
| MOD-005 | `com.meipao.edu.report` | 报表分析与决策驾驶舱 | §3.1.5 | FR-RPT-001~005 |
| MOD-006 | `com.meipao.edu.admin` | 系统管理与基础配置 | §3.1.6 | FR-ADM-001~005 |
| MOD-007 | `com.meipao.edu.core` | 共用基础设施 | — | 横切关注点 |

---

## 2. 模块详细定义

### MOD-001: 线索与学员管理 (`edu.crm`)

| 属性 | 值 |
|---|---|
| **职责** | 管理市场线索的全生命周期——从多渠道建档、自动查重、跟进记录到转化为正式学员；维护学员档案、转介绍关系链和顾问归属 |
| **依赖** | `edu.core`（唯一依赖） |
| **对外接口** | `StudentService.getById(Long)` — 提供学员基本信息（被 ENR/ACA/FIN/RPT 调用） |
| **FR 映射** | FR-CRM-001 多渠道线索建档 / FR-CRM-002 手工登记 / FR-CRM-003 自动查重 / FR-CRM-004 跟进记录 / FR-CRM-005 转介绍管理 |
| **Controller** | `LeadController`, `StudentController`, `ReferralController` |
| **核心 Entity** | `Lead`, `Student`, `FollowUpRecord`, `Referral` |
| **关键枚举** | `LeadStatus` (待跟进/跟进中/已转化/已流失), `StudentStatus` (在读/休学/结业/流失) |
| **SRS 引用** | SRS §3.1.1, §3.3.2 线索状态枚举 |

### MOD-002: 报名缴费与订单管理 (`edu.enrollment`)

| 属性 | 值 |
|---|---|
| **职责** | 课程推荐、选班、订单生成与编辑、优惠自动应用、多元化支付（微信/支付宝）、支付即记录、财务一键对账、自动匹配与降级匹配、异常收款处理 |
| **依赖** | `edu.core`, `edu.crm` |
| **对外接口** | `OrderService.createOrder(OrderRequest)` / `PaymentService.reconcilePayment(PaymentCallback)` |
| **FR 映射** | FR-ENR-001 课程推荐 / FR-ENR-002 报名订单 / FR-ENR-003 优惠审批 / FR-ENR-004 支付即记录 / FR-ENR-005 一键对账 |
| **Controller** | `CourseController`, `OrderController`, `PaymentController`, `ReconciliationController` |
| **核心 Entity** | `Course`, `Class`, `Order`, `Payment` |
| **关键枚举** | `OrderStatus` (待支付/已支付/已取消/已退款), `PaymentStatus` (待确认/已收款/异常待处理/待认领/已退款) |
| **外部集成** | 微信支付 API v3、支付宝商家中心 API |
| **SRS 引用** | SRS §3.1.2, §3.2.3 IF-SW-001/002, §3.3.2 订单状态/收款状态枚举 |

### MOD-003: 教务排课与消课管理 (`edu.academic`)

| 属性 | 值 |
|---|---|
| **职责** | 学期排课与冲突检测、班级名额实时管控与锁定、调课管理多方协同闭环（通知→确认→二次协调→超时释放）、课程考勤（扫码签到）、课时自动消耗、请假/调课补偿课时处理 |
| **依赖** | `edu.core`（唯一依赖，通过 `StudentService` 接口读取学员信息） |
| **对外接口** | `ScheduleService.checkConflict(ScheduleRequest)` / `AttendanceService.consumeHours(Long lessonId)` |
| **FR 映射** | FR-ACA-001 排课冲突 / FR-ACA-002 名额管控 / FR-ACA-003 调课协同 / FR-ACA-004 考勤消课 / FR-ACA-005 请假补偿 |
| **Controller** | `ScheduleController`, `RescheduleController`, `AttendanceController`, `LeaveController` |
| **核心 Entity** | `Schedule`, `Lesson`, `Attendance`, `RescheduleRequest`, `LeaveRequest` |
| **关键枚举** | `RescheduleStatus` (待确认/已同意/已反对/已超时/二次协调中/已取消), `AttendanceStatus` (正常/迟到/缺席/请假), `HourType` (正常/赠送/补课) |
| **内部工具** | 二维码签到（30min 有效期）、催办定时任务（超过截止时间自动释放名额） |
| **SRS 引用** | SRS §3.1.3, §3.3.2 调课/考勤/课时枚举 |

### MOD-004: 财务管理与核算 (`edu.finance`)

| 属性 | 值 |
|---|---|
| **职责** | 收费台账自动生成与多维度查询、退费多级审批流程（主管→财务→[校长加签]）、退款执行（原路退回）、教师薪酬自动核算、欠费预警与协同提醒 |
| **依赖** | `edu.core`, `edu.enrollment` |
| **对外接口** | `LedgerService.generateLedger(Order)` / `RefundService.processRefund(RefundRequest)` / `SalaryService.calculate(Long teacherId, Month month)` |
| **FR 映射** | FR-FIN-001 收费台账 / FR-FIN-002 退费审批 / FR-FIN-003 教师薪酬 / FR-FIN-004 欠费预警 |
| **Controller** | `LedgerController`, `RefundController`, `SalaryController`, `ArrearsController` |
| **核心 Entity** | `Ledger`, `Refund`, `Salary`, `ArrearsAlert` |
| **关键枚举** | `RefundStatus` (申请中/主管审批中/财务复核中/校长加签中/已批准/已驳回/退款处理中/退款完成) |
| **SRS 引用** | SRS §3.1.4, §3.3.2 退费审批状态枚举 |

### MOD-005: 报表分析与决策驾驶舱 (`edu.report`)

| 属性 | 值 |
|---|---|
| **职责** | 核心指标动态驾驶舱（营收/续费率/满班率/退费率）、招生转化漏斗分析、续费率与教学运营分析、营销活动 ROI 分析、多校区营收对比与财务监控。所有查询为只读 |
| **依赖** | `edu.core`, `edu.enrollment`, `edu.finance`, `edu.academic`（跨模块只读查询） |
| **对外接口** | 无（该模块不被其他模块调用，仅提供 REST API 给前端） |
| **FR 映射** | FR-RPT-001 核心驾驶舱 / FR-RPT-002 转化漏斗 / FR-RPT-003 续费率分析 / FR-RPT-004 营销效果 / FR-RPT-005 营收对比 |
| **Controller** | `DashboardController`, `FunnelController`, `RetentionController`, `MarketingController`, `RevenueController` |
| **核心 VO** | `DashboardVO`, `FunnelVO`, `RetentionVO`, `RevenueComparisonVO` |
| **数据访问** | MyBatis 复杂 SQL（跨表聚合），禁止在 Service 中拼 SQL |
| **SRS 引用** | SRS §3.1.5 |

### MOD-006: 系统管理与基础配置 (`edu.admin`)

| 属性 | 值 |
|---|---|
| **职责** | 多校区数据隔离（应用层 campus_id 注入）、细粒度 RBAC 权限管理、全链路操作日志审计（@Auditable AOP）、系统配置与业务规则热更新、历史数据导入与迁移 |
| **依赖** | `edu.core`（唯一依赖） |
| **对外接口** | `AuditService.log(AuditEvent)` — 被所有模块通过 Spring Event 异步调用 / `ConfigService.get(String key)` — 提供运行时配置查询 |
| **FR 映射** | FR-ADM-001 数据隔离 / FR-ADM-002 RBAC 权限 / FR-ADM-003 日志审计 / FR-ADM-004 系统配置 / FR-ADM-005 历史数据导入 |
| **Controller** | `UserController`, `RoleController`, `AuditLogController`, `ConfigController`, `DataImportController` |
| **核心 Entity** | `User`, `Role`, `Permission`, `AuditLog`, `SystemConfig`, `ImportJob` |
| **横切注解** | `@RequireCampus`, `@Auditable`, `@RateLimit` |
| **SRS 引用** | SRS §3.1.6 |

### MOD-007: 共用基础设施 (`edu.core`)

| 属性 | 值 |
|---|---|
| **职责** | 提供所有模块共用的基础设施：统一响应体 (`ApiResponse<T>`)、统一异常处理 (`@ControllerAdvice` + `BusinessException`)、JWT 认证过滤器、`campus_id` 注入 AOP、通用分页 (`PageRequest`/`PageResponse`)、基础 Entity 抽象类 (`BaseEntity` 含 createdAt/updatedAt/deleted)、Redis 工具类、文件上传工具 |
| **依赖** | 零依赖（不依赖任何业务模块） |
| **对外接口** | 全部 public 接口（工具类、注解、基类） |
| **包结构** | `core.config/`, `core.security/`, `core.aop/`, `core.exception/`, `core.util/`, `core.base/` |
| **SRS 引用** | 横切——不直接对应单一 FR |

---

## 3. 模块间接口契约概要

| 调用方 | 被调用方 | 接口 | 调用方式 |
|---|---|---|---|
| ENR, ACA, FIN, RPT | CRM | `StudentService.getById()` | 同步方法调用 |
| FIN | ENR | `OrderService.getByOrderNo()` | 同步方法调用 |
| RPT | ENR | `OrderService.queryByDateRange()` | MyBatis 只读查询 |
| RPT | FIN | `LedgerService.queryByCampus()` | MyBatis 只读查询 |
| RPT | ACA | `ScheduleService.getOccupancyRate()` | MyBatis 只读查询 |
| 全部模块 | ADM | `AuditService.log()` | Spring Event 异步 |
| 全部模块 | ADM | `ConfigService.get()` | 同步方法调用 |
| 全部模块 | CORE | `ApiResponse`, `BaseEntity`, `BusinessException` | 编译期依赖 |

---

## 4. 模块边界检查清单

| 检查项 | 约束 |
|---|---|
| 模块间循环依赖 | 禁止（DTS 拓扑图验证，详见 DTS-EDU-V1） |
| Service 跨模块调用 | 仅通过接口，不直接访问其他模块的 Repository |
| 报表模块写操作 | 禁止——`edu.report` 为只读模块 |
| core 模块依赖业务模块 | 禁止——`edu.core` 为纯基础设施 |
| 模块内 SQL | SQL 全部在 Repository 层（JPA 方法命名 / MyBatis XML） |

---

*本 MDS 基于 ASD-EDU-V1 §2 模块划分正式定义，属于期末考核第 2 项交付物（D12 工程产物定义）。*
