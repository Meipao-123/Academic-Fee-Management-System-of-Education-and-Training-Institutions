# 教育培训机构教务收费管理系统

> **《高级软件设计实践》实训项目** — AI 赋能的全流程软件工程实践  
> 软件工程专业 · 大三实习实训 · 4 周 / 32 学时 / 2 学分

---

## 项目简介

本项目是《高级软件设计实践》课程的实训项目，以**教育培训机构教务收费管理系统**为案例，实践 AI 赋能的完整软件开发闭环：

```
需求获取 → 需求分析 → 需求规格说明 → 需求验证确认
    → 架构选型 → 约束设计 → AI 代码生成(v1)
    → 需求变更管理 → 代码变更维护(v2) → 逆向校验 → 设计资产归档
```

---

## 目录结构（Karpathy 四层知识库）

```
├── raw/notes/              # 第1层 · 原始笔记（涉众原话，不可修改）
├── wiki/
│   ├── summaries/          # 第2层 · 总结提炼（需求清单/UML/SRS初稿/Agent配置）
│   └── baselines/          # 第3层 · 基线版本（评审冻结后，不可修改不可删除）
├── archive/                # 第4层 · 归档（五层设计资产包）
├── compile.js              # 知识库编译验证脚本
├── 00_项目总作战计划.md     # 项目主控文档（20天排程/交付物/规范索引）
└── reasonix.toml           # Reasonix AI 代码生成配置
```

---

## 开发环境

| 工具 | 用途 |
|---|---|
| **Node.js** ≥ 18 | compile.js 校验脚本运行环境 |
| **Git** | 版本控制 |
| **Python** ≥ 3.10 | CrewAI 多智能体框架 (A1~A6) |
| **DeepSeek API** | AI 智能体语言模型 (`deepseek-v4-pro`) |
| **PlantUML** | UML 建模（用例图/活动图/时序图） |
| **n8n** | 工作流自动化编排 |
| **Reasonix** | AI 代码生成终端 |

---

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/Meipao-123/Academic-Fee-Management-System-of-Education-and-Training-Institutions.git
cd Academic-Fee-Management-System-of-Education-and-Training-Institutions

# 2. 配置密钥
cp .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY

# 3. 验证知识库编译
node compile.js
# 应输出：✅ 编译通过（0 错误 0 警告）

# 4. 启动 A1 涉众对话 Web 页面（D02 产物）
cd agents/web
python server.py
# 打开 http://localhost:8080
```

---

## 相关文档

- `《高级软件设计实践》实践任务书.docx` — 课程任务书（周历/交付物/评分标准）
- `《高级软件设计实践》讲义.docx` — 课程讲义（17 节方法论详解）
- `00_项目总作战计划 (2)(1).md` — 项目主控文档（每日排程/决策记录/进度看板）
- `实践规范文档/` — 14 份 AI 工程规范（SRS/ADR/ASD/MDS/DTS/TLCD/OAS/CR/CIA/CRR/RCR 生成规范）

---

## 进度

| 阶段 | 日期 | 状态 |
|---|---|---|
| 第 1 周 · 需求工程启动 | 06-15 ~ 06-19 | 🔄 D01 完成 |
| 第 2 周 · 建模→SRS→基线 | 06-22 ~ 06-26 | ⏳ 待开始 |
| 第 3 周 · 架构设计 + v1 代码 | 06-29 ~ 07-03 | ⏳ 待开始 |
| 第 4 周 · 变更闭环 + 归档 + 答辩 | 07-06 ~ 07-10 | ⏳ 待开始 |

---

## 维护者

- GitHub: [Meipao-123](https://github.com/Meipao-123)
- 项目仓库: [Academic-Fee-Management-System-of-Education-and-Training-Institutions](https://github.com/Meipao-123/Academic-Fee-Management-System-of-Education-and-Training-Institutions.git)
