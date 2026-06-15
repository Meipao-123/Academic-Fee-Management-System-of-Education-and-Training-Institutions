#!/usr/bin/env node
/**
 * compile.js — Obsidian 知识库编译验证脚本（Karpathy 四层架构）
 *
 * 四类检查（只验证不修正）：
 *   1. 结构检查 — 四层目录是否存在
 *   2. 命名检查 — raw/notes/ 下文件是否匹配 {涉众角色}-{YYYYMMDD-HHMM}-需求记录.md
 *   3. 链接检查 — Markdown 中的 [[wikilink]] 和 [text](path) 目标是否存在
 *   4. 基线一致性 — wiki/baselines/ 下每个基线目录是否有 SRS-正式版.md
 *
 * 用法：node compile.js [--strict]
 *   --strict  命名不规范的警告也视为错误（exit code 1）
 *   默认      命名不规范仅警告，不阻塞
 *
 * 退出码：0 = 通过（0 错误），1 = 有错误需要修正
 */

const fs = require('fs');
const path = require('path');

// ── 配置 ──────────────────────────────────────────────────
const ROOT = __dirname;
const LAYERS = {
  raw:   path.join(ROOT, 'raw', 'notes'),
  wikiSummaries: path.join(ROOT, 'wiki', 'summaries'),
  wikiBaselines: path.join(ROOT, 'wiki', 'baselines'),
  archive: path.join(ROOT, 'archive'),
};
const STRICT = process.argv.includes('--strict');

// ── 状态 ──────────────────────────────────────────────────
let errors = 0;
let warnings = 0;
let filesChecked = 0;

// ── 工具函数 ──────────────────────────────────────────────
function log(level, msg) {
  const prefix = { err: '❌ 错误', warn: '⚠️  警告', ok: '✅', info: '📋' }[level] || '';
  console.log(`  ${prefix}  ${msg}`);
}

function error(msg) { log('err', msg); errors++; }
function warn(msg)  { if (STRICT) { error(msg); } else { log('warn', msg); warnings++; } }
function ok(msg)    { log('ok', msg); }
function info(msg)  { log('info', msg); }

function dirExists(p) {
  try { return fs.statSync(p).isDirectory(); } catch { return false; }
}

function listMdFiles(dir) {
  if (!dirExists(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter(e => e.isFile() && e.name.endsWith('.md'))
    .map(e => e.name);
}

function listDirs(dir) {
  if (!dirExists(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter(e => e.isDirectory())
    .map(e => e.name);
}

function collectMdFilesRecursive(dir) {
  if (!dirExists(dir)) return [];
  const result = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      result.push(...collectMdFilesRecursive(full));
    } else if (e.isFile() && e.name.endsWith('.md')) {
      result.push(full);
    }
  }
  return result;
}

// ── 1. 结构检查 ───────────────────────────────────────────
function checkStructure() {
  info('【1. 结构检查】四层目录是否就位');
  const checks = [
    { label: 'raw/notes/',      dir: LAYERS.raw },
    { label: 'wiki/summaries/', dir: LAYERS.wikiSummaries },
    { label: 'wiki/baselines/', dir: LAYERS.wikiBaselines },
    { label: 'archive/',        dir: LAYERS.archive },
  ];
  for (const { label, dir } of checks) {
    if (dirExists(dir)) {
      ok(`${label} 存在`);
    } else {
      error(`${label} 缺失 — 请创建该目录`);
    }
  }
}

// ── 2. 命名检查 ───────────────────────────────────────────
const NOTE_PATTERN = /^(.+)-(\d{8}-\d{4})-需求记录\.md$/;
// 允许的角色名称（宽松匹配，含中文）
const VALID_ROLES = ['课程顾问', '教务老师', '财务人员', '财务', '校长', '系统管理员'];

function checkNaming() {
  info('【2. 命名检查】raw/notes/ 文件命名规范');
  const files = listMdFiles(LAYERS.raw);
  if (files.length === 0) {
    warn('raw/notes/ 下暂无文件（D03 需求获取后会有文件写入）');
    return;
  }
  for (const f of files) {
    filesChecked++;
    const match = f.match(NOTE_PATTERN);
    if (!match) {
      error(`raw/notes/${f} — 命名不符合格式：应为 {涉众角色}-{YYYYMMDD-HHMM}-需求记录.md`);
      continue;
    }
    const role = match[1];
    const ts = match[2];
    // 时间戳基本校验：年月日-时分
    const [datePart, timePart] = ts.split('-');
    if (!/^\d{8}$/.test(datePart) || !/^\d{4}$/.test(timePart)) {
      error(`raw/notes/${f} — 时间戳格式错误：应为 YYYYMMDD-HHMM`);
      continue;
    }
    ok(`raw/notes/${f}  ✓`);
  }
}

// ── 3. 链接检查 ───────────────────────────────────────────
function checkLinks() {
  info('【3. 链接检查】Markdown 内部链接有效性');
  const allMd = collectMdFilesRecursive(ROOT)
    .filter(p => !p.includes('node_modules') && !p.includes('.codegraph') && !p.includes('.reasonix'));

  const mdFileSet = new Set(allMd.map(p => path.resolve(p)));
  let linkCount = 0;
  let brokenCount = 0;

  for (const filePath of allMd) {
    const content = fs.readFileSync(filePath, 'utf8');
    const dir = path.dirname(filePath);

    // 匹配 [text](target) 行内链接
    const inlineRegex = /\[([^\]]*)\]\(([^)]+)\)/g;
    let m;
    while ((m = inlineRegex.exec(content)) !== null) {
      const target = m[2];
      // 跳过外部 URL 和锚点
      if (target.startsWith('http://') || target.startsWith('https://') || target.startsWith('#')) continue;
      // 跳过 mailto
      if (target.startsWith('mailto:')) continue;

      linkCount++;
      // 处理 fragment (#)
      const [cleanTarget] = target.split('#');
      if (!cleanTarget) continue; // 纯锚点

      const resolved = path.resolve(dir, cleanTarget);
      if (cleanTarget.endsWith('.md') && !mdFileSet.has(resolved)) {
        // 检查是否是目录（目标可能是文件夹）
        if (!dirExists(resolved.replace(/\.md$/, '')) && !fs.existsSync(resolved)) {
          brokenCount++;
          const rel = path.relative(ROOT, filePath);
          warn(`${rel} → ${target}（目标不存在）`);
        }
      }
    }

    // 匹配 [[wikilink]] 双向链接
    const wikiRegex = /\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]/g;
    while ((m = wikiRegex.exec(content)) !== null) {
      linkCount++;
      const targetName = m[1].trim();
      // 尝试找同名 .md 文件
      const candidates = [
        path.resolve(dir, targetName + '.md'),
        path.resolve(ROOT, targetName + '.md'),
        path.resolve(LAYERS.raw, targetName + '.md'),
        path.resolve(LAYERS.wikiSummaries, targetName + '.md'),
        path.resolve(LAYERS.wikiBaselines, targetName + '.md'),
      ];
      const found = candidates.some(c => mdFileSet.has(c));
      if (!found) {
        brokenCount++;
        const rel = path.relative(ROOT, filePath);
        warn(`${rel} → [[${targetName}]]（未找到目标 .md 文件）`);
      }
    }
  }

  if (linkCount === 0) {
    ok('暂无内部链接（文件较少时正常）');
  } else if (brokenCount === 0) {
    ok(`共 ${linkCount} 个内部链接，全部有效`);
  }
}

// ── 4. 基线一致性检查 ──────────────────────────────────────
function checkBaselines() {
  info('【4. 基线一致性】wiki/baselines/ 每个基线目录结构');
  const baselineDirs = listDirs(LAYERS.wikiBaselines)
    .filter(d => /^BL-\d{8}-\d{2}$/.test(d));

  if (baselineDirs.length === 0) {
    ok('暂无基线目录（D09 创立基线后会有目录写入）');
    return;
  }

  for (const bd of baselineDirs) {
    const basePath = path.join(LAYERS.wikiBaselines, bd);
    const srsPath = path.join(basePath, 'SRS-正式版.md');
    if (fs.existsSync(srsPath)) {
      ok(`${bd}/SRS-正式版.md  ✓`);
    } else {
      error(`${bd}/ 缺少 SRS-正式版.md`);
    }
    filesChecked++;
  }
}

// ── 主流程 ─────────────────────────────────────────────────
console.log();
console.log('═══════════════════════════════════════════');
console.log('  compile.js · 知识库编译验证');
console.log('  Karpathy 四层架构 — 只验证不修正');
console.log('═══════════════════════════════════════════');
console.log(`  根目录: ${ROOT}`);
console.log();

checkStructure();
console.log();
checkNaming();
console.log();
checkLinks();
console.log();
checkBaselines();

// ── 汇总 ───────────────────────────────────────────────────
console.log();
console.log('───────────────────────────────────────────');
console.log(`  检查文件: ${filesChecked} 个`);
console.log(`  错误: ${errors}  |  警告: ${warnings}`);
if (errors === 0 && warnings === 0) {
  console.log('  结论: ✅ 编译通过（0 错误 0 警告）');
} else if (errors === 0) {
  console.log(`  结论: ✅ 编译通过（0 错误 ${warnings} 警告）`);
} else {
  console.log(`  结论: ❌ 编译失败（${errors} 错误，请修正后重新运行）`);
}
console.log('───────────────────────────────────────────');
console.log();

process.exit(errors > 0 ? 1 : 0);
