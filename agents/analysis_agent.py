# -*- coding: utf-8 -*-
"""
analysis_agent.py - A2 需求分析智能体

职责:
  1. 读取 raw/notes/ 下所有需求获取记录
  2. 检测 模糊/不一致/矛盾/冲突 四类质量问题
  3. 输出 需求问题清单 + 回退记录 到 wiki/summaries/

用法:
  python agents/analysis_agent.py
"""

import os
import re
import json
from pathlib import Path

# 确保项目根目录在 sys.path 中
import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.llm_config import chat

# -- 配置 -------------------------------------------------------
RAW_DIR = ROOT / "raw" / "notes"
OUT_DIR = ROOT / "wiki" / "summaries"
BATCH_SIZE = 3000  # 每次发送给 API 的最大字符数


# -- A2 系统提示词 -----------------------------------------------
SYSTEM_PROMPT = (
    '你是一个需求分析智能体(A2),负责对已获取的需求记录进行质量审查。\n'
    '\n'
    '## 你的检测维度(四类问题)\n'
    '1. **模糊**: 使用了模糊词汇(大概/可能/差不多/一般/左右/基本上/一般来说),缺少具体数值或明确规则\n'
    '2. **不一致**: 同一涉众在不同轮次中对同一事物的描述前后不同(如前面说A规则,后面说B规则)\n'
    '3. **矛盾**: 两个不同的描述在逻辑上无法同时成立\n'
    '4. **冲突**: 不同涉众之间对同一事物的需求存在对立(跨文件分析时检测)\n'
    '\n'
    '## 输出格式\n'
    '请对每条需求逐模块分析,按以下格式输出:\n'
    '\n'
    '### 模块: {模块名}\n'
    '- [问题类型] 原文: "{原文摘要}" | 问题: {具体问题描述} | 建议: {追问建议}\n'
    '\n'
    '## 汇总\n'
    '最后输出一个汇总表:\n'
    '| 涉众 | 模糊 | 不一致 | 矛盾 | 冲突 | 总计 |\n'
    '|------|------|--------|------|------|------|\n'
)


def load_records():
    """加载 raw/notes/ 下所有需求记录,提取涉众发言"""
    records = {}
    for f in sorted(RAW_DIR.glob("*.md")):
        if f.name == ".gitkeep":
            continue
        content = f.read_text(encoding="utf-8")
        # 提取涉众发言行
        stakeholder_lines = []
        for line in content.split("\n"):
            if line.startswith("**涉众**"):
                stakeholder_lines.append(line)
        # 提取涉众名称(从文件名)
        name = f.stem.split("-需求获取")[0].split("-")[0].strip()
        records[name] = {
            "file": f.name,
            "full_text": content,
            "stakeholder_text": "\n".join(stakeholder_lines),
            "line_count": len(stakeholder_lines),
        }
    return records


def analyze_stakeholder(name, info):
    """分析单个涉众的需求记录"""
    text = info["stakeholder_text"]
    full = info["full_text"]

    # 如果文本太长,按 BATCH_SIZE 分段
    chunks = []
    if len(full) > BATCH_SIZE * 2:
        # 只用涉众发言 + 上下文各 3000 字符
        chunks = [full[i:i + BATCH_SIZE] for i in range(0, min(len(full), BATCH_SIZE * 3), BATCH_SIZE)]
    else:
        chunks = [full]

    all_findings = []
    for idx, chunk in enumerate(chunks):
        chunk_label = "(第%d段)" % (idx + 1) if len(chunks) > 1 else ""
        user_msg = (
            "请分析以下涉众 %s 的需求记录%s,检测**模糊/不一致/矛盾**问题。\n\n"
            "---\n%s\n---\n"
        ) % (name, chunk_label, chunk)

        try:
            result = chat(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.3,
                max_tokens=4096,
            )
            all_findings.append(result["content"])
            print("  [A2] %s 分析完成 (token: %s)" % (name, result.get("usage", {}).get("total_tokens", "?")))
        except Exception as e:
            print("  [A2] %s 分析失败: %s" % (name, e))
            all_findings.append("分析失败: %s" % str(e))

    return "\n\n".join(all_findings)


def analyze_cross_stakeholder(records):
    """跨涉众冲突检测: 将5份记录的摘要一起发给 API"""
    summaries = []
    for name, info in records.items():
        # 取每份记录的前 600 字符作为摘要
        summary = info["stakeholder_text"][:600]
        summaries.append("### %s\n%s\n" % (name, summary))

    combined = "\n".join(summaries)
    user_msg = (
        "以下是5类涉众的需求摘要。请检测**跨涉众冲突**: 不同涉众对同一功能/规则是否存在对立需求。\n\n"
        "%s\n\n"
        "请列出所有发现的冲突点,格式: 涉众A vs 涉众B | 冲突主题 | 具体描述\n"
    ) % combined

    try:
        result = chat(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        print("  [A2] 跨涉众冲突检测完成")
        return result["content"]
    except Exception as e:
        print("  [A2] 跨涉众分析失败: %s" % e)
        return "跨涉众分析失败: %s" % str(e)


def generate_report(records, findings, cross_findings):
    """生成需求问题清单 + 回退记录"""
    timestamp = "20260617-2000"

    # -- 需求问题清单 -------------------------------------------
    issue_report = (
        "# 需求问题清单 - v1.0\n\n"
        "> 生成日期: %s\n"
        "> 分析范围: raw/notes/ 下 5 份需求获取记录\n"
        "> 分析方法: A2 需求分析智能体(四类检测: 模糊/不一致/矛盾/冲突)\n\n"
        "---\n\n"
    ) % timestamp

    # 按涉众列出
    for name, info in records.items():
        issue_report += "## %s\n\n" % name
        issue_report += "- 文件: `%s`\n" % info["file"]
        issue_report += "- 涉众发言行数: %d\n\n" % info["line_count"]
        if name in findings:
            issue_report += findings[name] + "\n\n"
        else:
            issue_report += "(分析结果待补充)\n\n"
        issue_report += "---\n\n"

    # 跨涉众冲突
    issue_report += "## 跨涉众冲突\n\n"
    issue_report += cross_findings + "\n\n"
    issue_report += "---\n\n"

    # -- 回退记录 -----------------------------------------------
    rollback_report = (
        "# 回退记录 - v1.0\n\n"
        "> 生成日期: %s\n"
        "> 说明: 以下需求因存在模糊/不一致/矛盾/冲突问题,需回退至对应涉众重新确认\n\n"
        "---\n\n"
    ) % timestamp

    # 从 findings 中提取需要回退的问题(模糊/不一致/矛盾)
    rollback_count = 0
    for name, text in findings.items():
        lines = text.split("\n")
        problem_lines = [
            l for l in lines
            if any(tag in l for tag in ["模糊]", "不一致]", "矛盾]", "冲突]"])
        ]
        if problem_lines:
            rollback_report += "## %s 需回退确认\n\n" % name
            for line in problem_lines:
                rollback_report += "- %s\n" % line.strip("- ")
                rollback_count += 1
            rollback_report += "\n"

    if rollback_count == 0:
        rollback_report += "> 当前未检测到需要回退的问题。\n\n"

    rollback_report += "---\n\n"
    rollback_report += "回退问题总数: %d\n" % rollback_count

    return issue_report, rollback_report


def main():
    print("=" * 60)
    print("  A2 需求分析智能体 - 启动")
    print("=" * 60)

    # 1. 加载记录
    records = load_records()
    print("\n[1/4] 已加载 %d 份需求记录:" % len(records))
    for name, info in records.items():
        print("  - %s: %d 行涉众发言" % (name, info["line_count"]))

    # 2. 逐涉众分析
    print("\n[2/4] 逐涉众分析中...")
    findings = {}
    for name, info in records.items():
        findings[name] = analyze_stakeholder(name, info)

    # 3. 跨涉众冲突检测
    print("\n[3/4] 跨涉众冲突检测中...")
    cross = analyze_cross_stakeholder(records)

    # 4. 生成报告
    print("\n[4/4] 生成报告中...")
    issue_report, rollback_report = generate_report(records, findings, cross)

    # 写入文件
    issue_path = OUT_DIR / "需求问题清单-v1.0.md"
    rollback_path = OUT_DIR / "回退记录-v1.0.md"

    issue_path.write_text(issue_report, encoding="utf-8")
    rollback_path.write_text(rollback_report, encoding="utf-8")

    print("\n" + "=" * 60)
    print("  A2 分析完成!")
    print("  需求问题清单: %s" % issue_path)
    print("  回退记录:     %s" % rollback_path)
    print("=" * 60)


if __name__ == "__main__":
    main()
