# n8n 工作流 1 — 需求开发全流程

**工作流名称**: 培训机构教务收费管理系统 — 需求工程流水线
**工作流 ID**: req-dev-pipeline-v1
**生成日期**: 2026-06-24
**编制人**: A5-需求验证智能体
**对应章节**: 作战计划 §2.2 七类AI智能体 + §5 D03~D09

---

## 1. 工作流概述

本工作流实现了从需求获取到基线创立的**完整需求工程流水线**，包含 7 类 AI 智能体的自动调度、人工审批节点和回退反馈环。

### 流水线拓扑

```
                    ┌─ A1-课程顾问 ──┐
                    ├─ A1-教务老师 ──┤
  [Webhook触发] ──→ ├─ A1-财务人员 ──┤ ──→ [A2 需求分析] ──→ [A3 UML建模]
                    ├─ A1-校长     ──┤        │  发现问题?
                    └─ A1-系统管理 ──┘        ↓ (是)
                                         回退对应A1重获取
                         
  [A3 UML建模] ──→ [A4 SRS生成] ──→ [A5 需求验证] ──→ [CCB 人工审批]
                       ↑  发现问题?        │  发现问题?         │
                       └────回退───────────┘                   │
                                           通过 ↓              │ 驳回 ↓
                                       [A6 基线创立]    回退 A4 修订
                                            ↓
                                       [通知: 完成]
```

---

## 2. 节点链路详解

### 节点 1: Webhook 触发器
| 属性 | 值 |
|---|---|
| 类型 | Webhook |
| 触发方式 | POST 请求 |
| 路径 | `/pipeline/req-dev/start` |
| 输入参数 | `{ project: string, stakeholders: string[] }` |
| 说明 | 外部系统或手动调用此端点一键启动全流程 |

### 节点 2~6: A1 需求获取（5 并行）
| 属性 | 值 |
|---|---|
| 类型 | HTTP Request (并行执行) |
| 各节点调用 | 对应涉众的 A1 Agent API |
| 输出 | `raw/notes/{涉众}-需求记录.md` |

| 节点 | API 端点 | 涉众 |
|---|---|---|
| A1-CC | `/api/agent/a1/course-consultant` | 课程顾问 |
| A1-AA | `/api/agent/a1/academic-affairs` | 教务老师 |
| A1-FN | `/api/agent/a1/finance` | 财务人员 |
| A1-PR | `/api/agent/a1/principal` | 校长 |
| A1-SA | `/api/agent/a1/system-admin` | 系统管理员 |

### 节点 7: A2 需求分析
| 属性 | 值 |
|---|---|
| 类型 | HTTP Request + Switch |
| 调用 | `/api/agent/a2/analyze` |
| 输入 | 5 份 `raw/notes/` 汇总 |
| 输出 | `需求问题清单-v1.0.md` |
| 分支 | 发现问题 → 触发回退通知；无问题 → 进入 A3 |

### 节点 8: 回退处理（A2 发现问题时）
| 属性 | 值 |
|---|---|
| 类型 | Switch + HTTP Request |
| 条件 | A2 输出中 `issues.length > 0` |
| 动作 | 针对有问题的涉众，重新调用对应 A1 Agent 进行补充获取 |

### 节点 9: A3 UML 建模
| 属性 | 值 |
|---|---|
| 类型 | HTTP Request |
| 调用 | `/api/agent/a3/model` |
| 输入 | `需求问题清单-v1.0.md` |
| 输出 | `UML用例图-v1.0.puml` + 3 份活动图 |
| 说明 | 生成 PlantUML 格式的用例图和活动图 |

### 节点 10: A4 SRS 生成
| 属性 | 值 |
|---|---|
| 类型 | HTTP Request |
| 调用 | `/api/agent/a4/generate-srs` |
| 输入 | `raw/notes/` + 问题清单 + UML 模型 |
| 输出 | `SRS-v1.x.md` |
| 说明 | 严格遵循 IEEE 830 标准生成 SRS 初稿 |

### 节点 11: A5 需求验证
| 属性 | 值 |
|---|---|
| 类型 | HTTP Request + Switch |
| 调用 | `/api/agent/a5/verify` |
| 输入 | SRS 初稿 + `raw/notes/` + 问题清单 + UML |
| 输出 | `验证报告-v2.x.md` |
| 分支 | 发现 Blocker → 回退 A4；无 Blocker → 进入 CCB |

### 节点 12: 回退处理（A5 发现问题时）
| 属性 | 值 |
|---|---|
| 类型 | Switch + HTTP Request |
| 条件 | A5 报告中 Blocker > 0 |
| 动作 | 将问题清单推送给 A4，触发 SRS 修订 |

### 节点 13: CCB 人工审批
| 属性 | 值 |
|---|---|
| 类型 | Webhook Wait (人工节点) |
| 等待路径 | `/pipeline/ccb/approve` |
| 审批选项 | 批准 → 进入 A6；驳回 → 回退 A4 |
| 超时 | 72 小时无响应自动提醒 |
| 说明 | CCB（变更控制委员会）由人工审批，对应作战计划 §2.2 中的人工审批节点 |

### 节点 14: A6 基线创立
| 属性 | 值 |
|---|---|
| 类型 | HTTP Request |
| 调用 | `/api/agent/a6/baseline` |
| 输入 | 审批通过的 SRS + 验证报告 |
| 输出 | `wiki/baselines/BL-YYYYMMDD-NN/` 目录 |
| 动作 | 冻结 SRS 为正式基线、生成 RTM、创建差异文档 |

### 节点 15: 完成通知
| 属性 | 值 |
|---|---|
| 类型 | Slack / Email / Webhook |
| 动作 | 通知项目组：需求基线已创立 |
| 内容 | 基线编号、SRS 版本、验证结论、Blocker/Major/Minor 计数 |

---

## 3. 反馈环设计

| 环编号 | 触发条件 | 回退目标 | 动作 |
|---|---|---|---|
| FB-1 | A2 检测到模糊/不一致/矛盾 | 对应 A1 | 补充获取该涉众需求 |
| FB-2 | A5 检测到 Blocker 级问题 | A4 | 修订 SRS 对应章节 |
| FB-3 | CCB 驳回 | A4（或更上游） | 按 CCB 意见修订后重新验证 |

### 反馈环防无限循环

| 机制 | 说明 |
|---|---|
| 最大回退次数 | 每个节点最多回退 3 次，超过则升级为人工介入 |
| 回退计数 | 每次回退在 payload 中递增 `retry_count` |
| 升级通知 | 回退超过 3 次 → 推送 Slack/Email 给项目管理者 |

---

## 4. 与作战计划的对应

| 作战计划步骤 | n8n 节点 | 说明 |
|---|---|---|
| D03~D04 A1 需求获取 | 节点 2~6 | 5 涉众并行获取 |
| D05 A2 需求分析 | 节点 7~8 | 四类检测 + 回退 |
| D06 A3 UML 建模 | 节点 9 | PlantUML 生成 |
| D07 A4 SRS 生成 | 节点 10 | IEEE 830 标准 |
| D08 A5 交叉验证 | 节点 11~12 | 交叉验证 + 回退 |
| CCB 人工审批 | 节点 13 | Webhook Wait |
| D09 A6 基线创立 | 节点 14~15 | 冻结基线 + 通知 |

---

## 5. 使用方式

### 5.1 一键触发
```bash
curl -X POST https://n8n.example.com/webhook/pipeline/req-dev/start \
  -H "Content-Type: application/json" \
  -d '{"project": "EDU", "stakeholders": ["course-consultant","academic-affairs","finance","principal","system-admin"]}'
```

### 5.2 人工审批响应
```bash
curl -X POST https://n8n.example.com/webhook/pipeline/ccb/approve \
  -H "Content-Type: application/json" \
  -d '{"pipeline_id": "xxx", "decision": "approve", "comment": "批准基线化"}'
```

### 5.3 监控
- n8n 内置执行历史记录
- 每个节点输出写入知识库对应目录
- 异常/超时自动推送 Slack 通知

---

## 6. 输出物

| 文件 | 路径 |
|---|---|
| n8n 工作流 JSON | `wiki/summaries/n8n-需求开发全流程-v1.0.json` |
| 节点链路说明 | `wiki/summaries/n8n-需求开发全流程-v1.0.md`（本文档） |

---

*本文档随 n8n 工作流 JSON 一同交付，属于期中考核第 9 项交付物。*
