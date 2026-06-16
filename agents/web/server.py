"""
server.py — A1 涉众对话 Web 后端（Python 标准库，零 pip 依赖）

接口：
  GET  /api/agents        → 返回 5 个 Agent 列表
  POST /api/chat           → { agent_id, messages } → DeepSeek API → 返回回复
  GET  /                   → 提供 index.html 静态页面

启动：python agents/web/server.py  (从项目根目录)
       或 cd agents/web && python server.py
访问：http://localhost:8080
"""

import json
import sys
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# 确保项目根目录在 sys.path 中
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from agents.llm_config import chat

# ── 加载 5 个 Agent ────────────────────────────────────────────
AGENT_FILES = [
    "course_consultant_agent",
    "academic_affairs_agent",
    "finance_agent",
    "principal_agent",
    "system_admin_agent",
]

agents = []
agent_map = {}

for name in AGENT_FILES:
    mod = __import__(f"agents.{name}", fromlist=["ROLE", "GOAL", "MODULES", "build_prompt"])
    agent_id = name.replace("_agent", "") + "_interviewer"
    display_name = f"A1-{name.replace('_agent','').replace('_',' ').title()}-需求获取"
    info = {
        "id": agent_id,
        "name": display_name,
        "role": mod.ROLE,
        "goal": mod.GOAL,
        "modules": [m["module"] for m in mod.MODULES],
    }
    agents.append(info)
    agent_map[agent_id] = mod


# ── HTTP Handler ───────────────────────────────────────────────
class ChatHandler(SimpleHTTPRequestHandler):
    """自定义 HTTP 请求处理器"""

    def __init__(self, *args, **kwargs):
        # 静态文件从 web/ 目录提供
        web_dir = str(Path(__file__).resolve().parent)
        super().__init__(*args, directory=web_dir, **kwargs)

    # ── CORS ────────────────────────────────────────────────
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    # ── 路由分发 ────────────────────────────────────────────
    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/api/agents":
            self._json_response(200, agents)
            return

        # 默认：静态文件
        if path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        path = self.path.split("?")[0]

        if path == "/api/chat":
            self._handle_chat()
            return

        self.send_error(404, "Not Found")

    # ── POST /api/chat ──────────────────────────────────────
    def _handle_chat(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            agent_id = data.get("agent_id", "")
            messages = data.get("messages", [])

            if agent_id not in agent_map:
                self._json_response(400, {"error": f"未知 Agent: {agent_id}"})
                return

            if not messages or not isinstance(messages, list):
                self._json_response(400, {"error": "缺少 messages 参数"})
                return

            mod = agent_map[agent_id]
            system_prompt = mod.build_prompt()

            full_messages = [
                {"role": "system", "content": system_prompt},
                *messages,
            ]

            last_msg = messages[-1]["content"][:50] if messages else ""
            print(f"[chat] {mod.ROLE} ← {last_msg}...")

            result = chat(full_messages, temperature=0.7, max_tokens=2048)

            print(f"[chat] {mod.ROLE} → {result['content'][:50]}...")

            self._json_response(200, {
                "reply": result["content"],
                "usage": result.get("usage", {}),
            })

        except Exception as e:
            print(f"[chat] 错误: {e}")
            self._json_response(500, {"error": str(e)})

    # ── JSON 响应工具 ───────────────────────────────────────
    def _json_response(self, status: int, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    # ── 日志精简 ────────────────────────────────────────────
    def log_message(self, format, *args):
        # 忽略静态资源请求日志
        if "api" in args[0] or args[0].startswith("POST"):
            print(f"[http] {args[0]}")
        # 其他请求静默


# ── 启动 ───────────────────────────────────────────────────────
PORT = int(os.environ.get("PORT", 8080))

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════╗
║  A1 涉众对话 Web 服务已启动 (Python)              ║
║  地址：http://localhost:{PORT}                      ║
║  接口：GET /api/agents · POST /api/chat            ║
║  已加载 {len(agents)} 个 Agent                          ║
╚══════════════════════════════════════════════════╝
""")
    server = HTTPServer(("0.0.0.0", PORT), ChatHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] 服务已停止")
        server.server_close()
