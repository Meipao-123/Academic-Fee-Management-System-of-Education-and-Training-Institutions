# -*- coding: utf-8 -*-
"""
modeling_agent.py - A3 建模智能体

职责:
  1. 读取 raw/notes/ 需求记录 + wiki/summaries/需求问题清单
  2. 生成 PlantUML 用例图(Use Case Diagram)
  3. 生成核心活动图(Activity Diagram): 报名/退费/排课消课

用法:
  python agents/modeling_agent.py
  输出: wiki/summaries/UML用例图-v1.0.puml 等
"""

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.llm_config import chat

# -- 系统提示词 -------------------------------------------------
SYSTEM_PROMPT = (
    '你是一个 UML 建模智能体(A3),负责根据需求记录生成 PlantUML 图表代码。\n'
    '\n'
    '## 你的职责\n'
    '1. 从需求记录中提取 Actor(涉众)、Use Case(功能)、关系\n'
    '2. 生成 PlantUML 用例图代码(使用 @startuml/@enduml 包裹)\n'
    '3. 生成核心流程的 PlantUML 活动图代码\n'
    '\n'
    '## PlantUML 规范\n'
    '- 使用 left to right direction 横向布局\n'
    '- 使用 package 组织用例,按涉众分组\n'
    '- 使用 ..> 表示依赖,<|-- 表示继承\n'
    '- 使用 note right/left 添加注释\n'
    '- 活动图使用泳道(|阶段名|)分隔\n'
    '- 使用 Guard 条件 [条件] 标注分支\n'
    '\n'
    '## 输出格式\n'
    '直接输出 PlantUML 代码(不要额外解释)\n'
)


def generate_use_case_diagram():
    """从需求记录生成用例图(当前为手工绘制版本,AI可辅助迭代)"""
    # 用例图已手工绘制: wiki/summaries/UML用例图-v1.0.puml
    # 此函数为框架,后续可接入 AI 自动生成
    pass


def generate_activity_diagram(flow_name, raw_text):
    """从需求文本片段生成活动图"""
    user_msg = (
        '请根据以下需求描述,生成 %s 的 PlantUML 活动图。\n'
        '要求: 使用泳道(partition)分隔角色,使用 Guard 条件标注分支。\n\n'
        '---\n%s\n---\n'
    ) % (flow_name, raw_text[:3000])

    try:
        result = chat(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        return result["content"]
    except Exception as e:
        return "生成失败: %s" % str(e)


if __name__ == "__main__":
    print("A3 建模智能体")
    print("用例图: wiki/summaries/UML用例图-v1.0.puml (手工绘制)")
    print("活动图: wiki/summaries/UML报名缴费-活动图-v1.0.puml")
    print("活动图: wiki/summaries/UML退费流程-活动图-v1.0.puml")
    print("活动图: wiki/summaries/UML排课消课-活动图-v1.0.puml")
