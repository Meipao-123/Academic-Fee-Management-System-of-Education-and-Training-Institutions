# -*- coding: utf-8 -*-
"""
srs_agent.py - A4 需求文档生成智能体

职责:
  1. 读取 raw/notes/ 需求记录 + wiki/summaries/需求问题清单 + UML 图
  2. 按 IEEE 830 / GB/T 9385 标准生成软件需求规格说明书(SRS)
  3. 输出 SRS-v1.0.md 到 wiki/summaries/ (≥15000字)

用法:
  python agents/srs_agent.py
"""

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.llm_config import chat

SYSTEM_PROMPT = (
    '你是一个需求规格说明撰写智能体(A4),负责根据需求记录和问题清单生成SRS文档。\n'
    '\n'
    '## 输出结构(IEEE 830标准)\n'
    '1. 引言(目的/范围/定义/参考文献)\n'
    '2. 总体描述(产品视角/用户特征/约束/假设)\n'
    '3. 具体需求(功能需求FR/接口需求IR/数据需求DR/非功能需求NFR)\n'
    '4. 附录(待确认项/变更记录)\n'
    '\n'
    '## 格式规范\n'
    '- 每个需求编号为 FR/IR/DR/NFR-模块缩写-NNN\n'
    '- 模糊项标注为 [TBD: 待回退确认]\n'
    '- 需求溯源矩阵(RTM)引用 raw/notes 文件名\n'
)


def generate_srs(records_summary, issue_summary, uml_summary):
    """调用 LLM 生成 SRS"""
    user_msg = (
        '请根据以下素材生成软件需求规格说明书(SRS)初稿。\n\n'
        '## 需求记录摘要\n%s\n\n'
        '## 问题清单摘要\n%s\n\n'
        '## UML模型摘要\n%s\n\n'
        '要求:\n'
        '1. 按 IEEE 830 结构组织\n'
        '2. 每个功能需求编号为 FR-模块缩写-NNN\n'
        '3. 模糊项标注 [TBD: 待回退确认]\n'
        '4. 文档 ≥ 15000 字\n'
    ) % (records_summary, issue_summary, uml_summary)

    result = chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.4,
        max_tokens=8192,
    )
    return result["content"]


def load_summary():
    """加载所有输入素材的摘要"""
    raw_dir = ROOT / "raw" / "notes"
    summaries = []
    for f in sorted(raw_dir.glob("*.md")):
        if f.name == ".gitkeep":
            continue
        content = f.read_text(encoding="utf-8")
        name = f.stem.split("-需求获取")[0]
        # 取前 800 字符摘要
        summaries.append("### %s\n%s\n" % (name, content[:800]))
    return "\n".join(summaries)


def load_issue_summary():
    """加载问题清单摘要"""
    issue_path = ROOT / "wiki" / "summaries" / "需求问题清单-v1.0.md"
    if issue_path.exists():
        content = issue_path.read_text(encoding="utf-8")
        return content[:2000]
    return "(无)"


def load_uml_summary():
    """加载 UML 模型摘要"""
    summaries = ROOT / "wiki" / "summaries"
    uml_files = [
        "UML用例图-v1.0.puml",
    ]
    texts = []
    for f in uml_files:
        path = summaries / f
        if path.exists():
            texts.append("### %s\n%s" % (f, path.read_text(encoding="utf-8")[:800]))
    return "\n".join(texts) if texts else "(暂无UML)"


if __name__ == "__main__":
    print("A4 SRS 生成智能体")
    print("读取 raw/notes/ + 问题清单 + UML...")

    records = load_summary()
    issues = load_issue_summary()
    uml = load_uml_summary()

    print("调用 LLM 生成 SRS (约需30-60秒)...")
    srs = generate_srs(records, issues, uml)

    out_path = ROOT / "wiki" / "summaries" / "SRS-v1.0.md"
    out_path.write_text(srs, encoding="utf-8")
    print("SRS 已保存到: %s" % out_path)
    print("字数: %d" % len(srs))
