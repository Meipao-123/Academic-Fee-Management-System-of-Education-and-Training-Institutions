# -*- coding: utf-8 -*-
"""
modeling_agent.py - A3 UML 建模智能体 (AI 生成版)

职责:
  1. 读取 raw/notes/ 所有需求记录
  2. 调用 LLM 生成 PlantUML 用例图 + 核心活动图
  3. 输出到 wiki/summaries/ (覆盖旧版)

用法:
  python agents/modeling_agent.py
"""

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.llm_config import chat

OUT_DIR = ROOT / "wiki" / "summaries"
RAW_DIR = ROOT / "raw" / "notes"

SYSTEM_PROMPT = (
    '你是一个 UML 建模智能体(A3),负责根据需求记录生成 PlantUML 图表代码。\n'
    '\n'
    '## PlantUML 规范\n'
    '- 使用 @startuml/@enduml 包裹\n'
    '- 用例图: left to right direction, actor, usecase, package, ..> 依赖, <|-- 继承\n'
    '- 活动图: start/stop, if/else, partition(泳道), note right/left\n'
    '- 使用 skinparam 美化\n'
    '- 不要输出任何 PlantUML 代码以外的解释文字\n'
    '- 第一个字符必须是 @,最后一行必须是 @enduml\n'
)


def load_all_records():
    """加载所有需求记录的全文"""
    texts = []
    for f in sorted(RAW_DIR.glob("*.md")):
        if f.name == ".gitkeep":
            continue
        content = f.read_text(encoding="utf-8")
        name = f.stem.split("-需求获取")[0]
        texts.append((name, content))
    return texts


def generate_use_case(records):
    """生成用例图"""
    # 构建精简输入: 只发送每个涉众的前 2500 字符
    summaries = []
    for name, content in records:
        summaries.append("## %s\n%s" % (name, content[:2500]))
    combined = "\n\n".join(summaries)

    prompt = (
        '请根据以下5类涉众的需求记录,生成 PlantUML 用例图。\n'
        '要求:\n'
        '1. 5个 Actor: 课程顾问/教务老师/财务人员/校长/系统管理员\n'
        '2. 1个外部 Actor: 家长/学员\n'
        '3. 用 package 按涉众组织用例,覆盖所有提到的功能\n'
        '4. 标注跨涉众依赖关系(..>)\n'
        '5. 使用 left to right direction 横向布局\n\n'
        '---\n%s\n---\n'
    ) % combined

    result = chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=4096,
    )
    return result["content"]


def generate_activity(records, flow_name, stakeholder_filter, extra_instruction):
    """生成活动图"""
    # 筛选相关涉众的记录
    relevant = []
    for name, content in records:
        if name in stakeholder_filter:
            relevant.append("## %s\n%s" % (name, content[:2000]))
    combined = "\n\n".join(relevant)

    prompt = (
        '请根据以下需求记录,生成 %s 的 PlantUML 活动图。\n'
        '%s\n'
        '要求:\n'
        '1. 使用 partition(泳道) 分隔角色\n'
        '2. 使用 Guard 条件 [条件] 标注分支\n'
        '3. 在关键节点添加 note right/left 注释\n'
        '4. 覆盖正常流程+异常流程\n\n'
        '---\n%s\n---\n'
    ) % (flow_name, extra_instruction, combined)

    result = chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=4096,
    )
    return result["content"]


def extract_uml(response):
    """从 LLM 响应中提取 @startuml...@enduml 块"""
    start = response.find("@startuml")
    end = response.find("@enduml")
    if start >= 0 and end >= 0:
        return response[start:end + len("@enduml")]
    return response  # 返回原文


def main():
    print("=" * 60)
    print("  A3 UML 建模智能体 (AI 生成)")
    print("=" * 60)

    records = load_all_records()
    print("\n已加载 %d 份需求记录:" % len(records))
    for name, content in records:
        print("  - %s: %d 字符" % (name, len(content)))

    # ── 1. 用例图 ──────────────────────────────────────────
    print("\n[1/4] 生成用例图...")
    try:
        uc = generate_use_case(records)
        uc = extract_uml(uc)
        (OUT_DIR / "UML用例图-v1.0.puml").write_text(uc, encoding="utf-8")
        print("  ✅ UML用例图-v1.0.puml (%d 字符)" % len(uc))
    except Exception as e:
        print("  ❌ 用例图生成失败: %s" % e)

    # ── 2. 报名缴费活动图 ──────────────────────────────────
    print("\n[2/4] 生成报名缴费活动图...")
    try:
        pay = generate_activity(
            records, "报名缴费流程",
            ["Course Consultant", "Finance"],
            "请覆盖: 线索→试听→选课→优惠→缴费→订单→收入确认 全链路",
        )
        pay = extract_uml(pay)
        (OUT_DIR / "UML报名缴费-活动图-v1.0.puml").write_text(pay, encoding="utf-8")
        print("  ✅ UML报名缴费-活动图-v1.0.puml (%d 字符)" % len(pay))
    except Exception as e:
        print("  ❌ 报名缴费活动图生成失败: %s" % e)

    # ── 3. 退费流程活动图 ──────────────────────────────────
    print("\n[3/4] 生成退费流程活动图...")
    try:
        refund = generate_activity(
            records, "退费流程",
            ["Finance", "Principal"],
            "请覆盖: 申请→核查→金额计算→多级审批→原路退款→冲销→通知 全链路",
        )
        refund = extract_uml(refund)
        (OUT_DIR / "UML退费流程-活动图-v1.0.puml").write_text(refund, encoding="utf-8")
        print("  ✅ UML退费流程-活动图-v1.0.puml (%d 字符)" % len(refund))
    except Exception as e:
        print("  ❌ 退费流程活动图生成失败: %s" % e)

    # ── 4. 排课消课活动图 ──────────────────────────────────
    print("\n[4/4] 生成排课消课活动图...")
    try:
        sched = generate_activity(
            records, "排课与消课流程",
            ["Academic Affairs"],
            "请覆盖: 排课→冲突检测→考勤→消课→请假补课→课时统计→收入确认 全链路",
        )
        sched = extract_uml(sched)
        (OUT_DIR / "UML排课消课-活动图-v1.0.puml").write_text(sched, encoding="utf-8")
        print("  ✅ UML排课消课-活动图-v1.0.puml (%d 字符)" % len(sched))
    except Exception as e:
        print("  ❌ 排课消课活动图生成失败: %s" % e)

    print("\n" + "=" * 60)
    print("  A3 UML 建模完成!")
    print("  输出: wiki/summaries/UML*.puml (4 个文件)")
    print("=" * 60)


if __name__ == "__main__":
    main()
