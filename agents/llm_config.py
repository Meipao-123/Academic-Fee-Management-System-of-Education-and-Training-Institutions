"""
llm_config.py — 统一 LLM 配置（Python 版本）

从 .env 读取 DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL / DEEPSEEK_MODEL，
封装 chat(messages) 函数，供给 A1~A6 所有 Agent 使用。

直接调用 DeepSeek API HTTP，可与 CrewAI 框架配合。
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path


# ── 读取 .env ─────────────────────────────────────────────────
def _load_env() -> dict:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        print("[llm_config] ⚠️  .env 文件不存在，请从 .env.example 复制并填入密钥")
        return {}

    env = {}
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, val = line.partition("=")
            env[key.strip()] = val.strip()
    return env


ENV = _load_env()

# ── 配置 ──────────────────────────────────────────────────────
CONFIG = {
    "api_key":  ENV.get("DEEPSEEK_API_KEY", "sk-placeholder"),
    "base_url": ENV.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "model":    ENV.get("DEEPSEEK_MODEL", "deepseek-chat"),
}


# ── 核心：chat 函数 ────────────────────────────────────────────
def chat(messages: list[dict], temperature: float = 0.7, max_tokens: int = 4096, timeout: int = 60) -> dict:
    """
    调用 DeepSeek API 进行对话补全。

    Args:
        messages: [{"role": "system"|"user"|"assistant", "content": "..."}, ...]
        temperature: 采样温度 (0-2)
        max_tokens: 最大生成长度
        timeout: HTTP 请求超时秒数 (默认 60，SRS 等大输出建议 300)

    Returns:
        {"content": str, "usage": dict}
    """
    url = f"{CONFIG['base_url']}/v1/chat/completions"
    body = {
        "model": CONFIG["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CONFIG['api_key']}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else str(e)
        raise RuntimeError(f"DeepSeek API 错误 ({e.code}): {err_body}")

    choice = data.get("choices", [{}])[0]
    msg = choice.get("message", {})
    if not msg:
        raise RuntimeError(f"DeepSeek API 返回格式异常: {json.dumps(data, ensure_ascii=False)}")

    return {
        "content": msg.get("content", ""),
        "usage": data.get("usage", {}),
    }


# ── 连通性测试 ─────────────────────────────────────────────────
def test_connection() -> bool:
    """发送一条简单消息，测试 DeepSeek API 连通性。"""
    print("[llm_config] 测试连通性...")
    print(f"  Base URL: {CONFIG['base_url']}")
    print(f"  Model:    {CONFIG['model']}")
    print(f"  API Key:  {CONFIG['api_key'][:8]}***")

    try:
        result = chat(
            [{"role": "user", "content": '你好，请回复"连通成功"。只回复这四个字。'}],
            temperature=0,
            max_tokens=50,
        )
        print(f"  回复: {result['content'].strip()}")
        print(f"  Token 用量: {result['usage']}")
        print("[llm_config] ✅ 连通性测试通过")
        return True
    except Exception as e:
        print(f"[llm_config] ❌ 连通性测试失败: {e}")
        return False


if __name__ == "__main__":
    import sys
    ok = test_connection()
    sys.exit(0 if ok else 1)
