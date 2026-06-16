/**
 * llm_config.js — 统一 LLM 配置（Node.js 等效方案）
 *
 * 从 .env 读取 DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL / DEEPSEEK_MODEL，
 * 封装 chat(messages) 函数，供给 A1~A6 所有 Agent 使用。
 *
 * 用途：替代 CrewAI + LiteLLM 组合，直接用 DeepSeek API HTTP 调用。
 * 依据：作战计划 §8.4 — "本机等效方案落地"。
 */

const fs = require('fs');
const path = require('path');

// ── 读取 .env ──────────────────────────────────────────────
function loadEnv() {
  const envPath = path.join(__dirname, '..', '.env');
  if (!fs.existsSync(envPath)) {
    console.warn('[llm_config] ⚠️  .env 文件不存在，请从 .env.example 复制并填入密钥');
    return {};
  }
  const env = {};
  const content = fs.readFileSync(envPath, 'utf8');
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eqIdx = trimmed.indexOf('=');
    if (eqIdx === -1) continue;
    const key = trimmed.slice(0, eqIdx).trim();
    const val = trimmed.slice(eqIdx + 1).trim();
    env[key] = val;
  }
  return env;
}

const ENV = loadEnv();

// ── 配置 ───────────────────────────────────────────────────
const CONFIG = {
  apiKey:  ENV.DEEPSEEK_API_KEY  || 'sk-placeholder',
  baseUrl: ENV.DEEPSEEK_BASE_URL || 'https://api.deepseek.com',
  model:   ENV.DEEPSEEK_MODEL    || 'deepseek-chat',
};

// ── 核心：chat 函数 ─────────────────────────────────────────
/**
 * 调用 DeepSeek API 进行对话补全
 * @param {Array<{role:string, content:string}>} messages - 消息数组
 * @param {Object} [opts] - 可选参数
 * @param {number} [opts.temperature=0.7]
 * @param {number} [opts.max_tokens=4096]
 * @returns {Promise<{content:string, usage:Object}>}
 */
async function chat(messages, opts = {}) {
  const { temperature = 0.7, max_tokens = 4096 } = opts;

  const url = `${CONFIG.baseUrl}/v1/chat/completions`;
  const body = {
    model: CONFIG.model,
    messages,
    temperature,
    max_tokens,
    stream: false,
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${CONFIG.apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`DeepSeek API 错误 (${response.status}): ${errText}`);
  }

  const data = await response.json();
  const choice = data.choices && data.choices[0];
  if (!choice || !choice.message) {
    throw new Error(`DeepSeek API 返回格式异常: ${JSON.stringify(data)}`);
  }

  return {
    content: choice.message.content,
    usage: data.usage || {},
  };
}

/**
 * 测试连通性 — 发送一条简单消息，打印结果
 */
async function testConnection() {
  console.log(`[llm_config] 测试连通性...`);
  console.log(`  Base URL: ${CONFIG.baseUrl}`);
  console.log(`  Model:    ${CONFIG.model}`);
  console.log(`  API Key:  ${CONFIG.apiKey.slice(0, 8)}***`);

  try {
    const result = await chat([
      { role: 'user', content: '你好，请回复"连通成功"。只回复这四个字。' }
    ], { max_tokens: 50, temperature: 0 });
    console.log(`  回复: ${result.content.trim()}`);
    console.log(`  Token 用量:`, result.usage);
    console.log(`[llm_config] ✅ 连通性测试通过`);
    return true;
  } catch (err) {
    console.error(`[llm_config] ❌ 连通性测试失败: ${err.message}`);
    return false;
  }
}

// ── 导出 ───────────────────────────────────────────────────
module.exports = { chat, testConnection, CONFIG };

// ── 直接运行 node agents/llm_config.js 时执行连通性测试 ──────
if (require.main === module) {
  testConnection().then(ok => process.exit(ok ? 0 : 1));
}
