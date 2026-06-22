# -*- coding: utf-8 -*-
"""
verification_agent.py - A5 需求验证智能体

职责:
  1. 读取 SRS-v1.1.md + raw/notes/ + 需求问题清单 + UML
  2. 四维交叉验证:
     ① 历史需求比对: SRS 中每个 FR 是否能在 raw/notes 中找到涉众原话
     ② 问题清单比对: A2 检测出的问题是否在 SRS 中标记为 [TBD]
     ③ SRS 内部一致性: FR 编号连续性/术语一致性/无自相矛盾
     ④ UML 一致性: SRS 描述的流程是否与活动图一致
  3. 输出验证报告 wiki/summaries/验证报告-v1.0.md

用法:
  python agents/verification_agent.py
"""

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.llm_config import chat

OUT_DIR = ROOT / "wiki" / "summaries"
RAW_DIR = ROOT / "raw" / "notes"

SYSTEM_PROMPT = (
    '你是一个需求验证智能体(A5),负责对SRS文档进行四维交叉验证。\n'
    '\n'
    '## 验证维度\n'
    '① 历史需求比对: SRS中每个FR是否能在raw/notes中找到对应涉众原话\n'
    '② 问题清单比对: A2检测出的问题是否在SRS中被标记为[TBD]\n'
    '③ SRS内部一致性: FR编号连续、术语定义一致、无自相矛盾\n'
    '④ UML一致性: SRS描述的流程是否与活动图一致\n'
    '\n'
    '## 严重级别\n'
    '- Blocker: 必须修复才能基线\n'
    '- Major: 建议修复\n'
    '- Minor: 可豁免\n'
    '\n'
    '## 输出格式\n'
    '## 验证摘要\n'
    '| 维度 | 通过状态 | 问题数 | 最高级别 |\n'
    '|---|---|---|---|\n'
    '\n'
    '## 详细问题\n'
    '- [级别] 维度: 描述 | SRS位置 | 建议\n'
    '\n'
    '## 结论\n'
    '总体评价: ✅通过 / ⚠️需修订 / ❌不通过\n'
)


def load_srs():
    path = OUT_DIR / "SRS-v1.1.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(SRS未找到)"


def load_records():
    texts = []
    for f in sorted(RAW_DIR.glob("*.md")):
        if f.name == ".gitkeep":
            continue
        content = f.read_text(encoding="utf-8")
        name = f.stem.split("-需求获取")[0]
        texts.append("### %s\n%s" % (name, content[:2000]))
    return "\n\n".join(texts)


def load_issue_summary():
    path = OUT_DIR / "需求问题清单-v1.0.md"
    if path.exists():
        return path.read_text(encoding="utf-8")[:5000]
    return "(无)"


def load_uml_summary():
    summaries = OUT_DIR
    uml_files = [
        "UML用例图-v1.0.puml",
        "UML报名缴费-活动图-v1.0.puml",
        "UML退费流程-活动图-v1.0.puml",
        "UML排课消课-活动图-v1.0.puml",
    ]
    texts = []
    for f in uml_files:
        path = summaries / f
        if path.exists():
            texts.append("### %s\n```puml\n%s\n```" % (f, path.read_text(encoding="utf-8")[:2000]))
    return "\n\n".join(texts) if texts else "(暂无UML)"


def generate_verification_report(srs, records, issues, uml):
    user_msg = (
        '请对以下SRS文档进行四维交叉验证。\n\n'
        '## SRS-v1.1\n%s\n\n'
        '## raw/notes/ (原始需求)\n%s\n\n'
        '## 需求问题清单\n%s\n\n'
        '## UML 模型\n%s\n\n'
        '进行四维验证(历史比对/问题清单比对/内部一致性/UML一致性),'
        '按指定格式输出验证报告。\n'
    ) % (srs, records, issues, uml)

    result = chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
        max_tokens=8192,
        timeout=300,
    )
    return result["content"]


def main():
    print("=" * 60)
    print("  A5 需求验证智能体")
    print("=" * 60)

    print("\n[1/5] 加载 SRS-v1.1...")
    srs = load_srs()
    print("  SRS: %d 字符" % len(srs))

    print("[2/5] 加载 raw/notes...")
    records = load_records()
    print("  原始需求: %d 字符" % len(records))

    print("[3/5] 加载问题清单...")
    issues = load_issue_summary()
    print("  问题清单: %d 字符" % len(issues))

    print("[4/5] 加载 UML...")
    uml = load_uml_summary()
    print("  UML: %d 字符" % len(uml))

    print("[5/5] 生成验证报告 (约需30-60秒)...")
    try:
        report = generate_verification_report(srs, records, issues, uml)
        out_path = OUT_DIR / "验证报告-v1.0.md"
        out_path.write_text(report, encoding="utf-8")
        print("\n" + "=" * 60)
        print("  验证报告已保存: %s" % out_path)
        print("  字数: %d" % len(report))
        print("=" * 60)
    except Exception as e:
        print("  ❌ 验证报告生成失败: %s" % e)


if __name__ == "__main__":
    main()
