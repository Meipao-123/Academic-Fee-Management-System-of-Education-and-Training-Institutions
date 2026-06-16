/**
 * server.js — A1 涉众对话 Web 后端（Node.js 标准库，零依赖）
 *
 * 接口：
 *   GET  /api/agents        → 返回 5 个 Agent 列表
 *   POST /api/chat           → { agent_id, messages } → DeepSeek API → 返回回复
 *   GET  /                    → 提供 index.html 静态页面
 *
 * 启动：node agents/web/server.js
 * 访问：http://localhost:8080
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chat } = require('../llm_config');

// ── 加载 5 个 Agent ────────────────────────────────────────
const AGENTS_DIR = path.join(__dirname, '..');
const agentFiles = [
  'course_consultant_agent.js',
  'academic_affairs_agent.js',
  'finance_agent.js',
  'principal_agent.js',
  'system_admin_agent.js',
];

const agents = [];
const agentMap = {};

for (const file of agentFiles) {
  const a = require(path.join(AGENTS_DIR, file));
  agents.push({
    id: a.id,
    name: a.name,
    role: a.role,
    goal: a.goal,
    modules: a.modules.map(m => m.module),
  });
  agentMap[a.id] = a;
}

// ── MIME 类型 ──────────────────────────────────────────────
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
};

// ── HTTP 服务器 ────────────────────────────────────────────
const PORT = process.env.PORT || 8080;

const server = http.createServer(async (req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    return res.end();
  }

  const url = new URL(req.url, `http://localhost:${PORT}`);
  const method = req.method;

  // ── API 路由 ────────────────────────────────────────────
  if (url.pathname === '/api/agents' && method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    return res.end(JSON.stringify(agents));
  }

  if (url.pathname === '/api/chat' && method === 'POST') {
    try {
      const body = await readBody(req);
      const { agent_id, messages } = JSON.parse(body);

      if (!agent_id || !agentMap[agent_id]) {
        res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify({ error: `未知 Agent: ${agent_id}` }));
      }

      if (!messages || !Array.isArray(messages) || messages.length === 0) {
        res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify({ error: '缺少 messages 参数' }));
      }

      const agent = agentMap[agent_id];
      const systemPrompt = agent.buildPrompt();

      // 拼接：系统提示词 + 历史对话
      const fullMessages = [
        { role: 'system', content: systemPrompt },
        ...messages,
      ];

      console.log(`[chat] ${agent.name} ← ${messages[messages.length-1]?.content?.slice(0, 50)}...`);

      const result = await chat(fullMessages, { temperature: 0.7, max_tokens: 2048 });

      console.log(`[chat] ${agent.name} → ${result.content.slice(0, 50)}...`);

      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      return res.end(JSON.stringify({
        reply: result.content,
        usage: result.usage,
      }));
    } catch (err) {
      console.error('[chat] 错误:', err.message);
      res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
      return res.end(JSON.stringify({ error: err.message }));
    }
  }

  // ── 静态文件 ────────────────────────────────────────────
  let filePath = path.join(__dirname, url.pathname === '/' ? 'index.html' : url.pathname);
  const ext = path.extname(filePath);

  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    const content = fs.readFileSync(filePath);
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    return res.end(content);
  }

  // 404
  res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end('404 Not Found');
});

// ── 工具函数 ──────────────────────────────────────────────
function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', chunk => data += chunk);
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

// ── 启动 ──────────────────────────────────────────────────
server.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════╗
║  A1 涉众对话 Web 服务已启动                        ║
║  地址：http://localhost:${PORT}                      ║
║  接口：GET /api/agents · POST /api/chat            ║
║  已加载 ${agents.length} 个 Agent                          ║
╚══════════════════════════════════════════════════╝
`);
});
