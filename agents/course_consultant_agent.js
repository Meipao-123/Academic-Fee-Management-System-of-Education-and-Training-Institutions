/**
 * course_consultant_agent.js — A1 需求获取 Agent（采访方）
 * 采访对象：课程顾问
 *
 * CrewAI 等效定义：Role + Goal + Backstory
 * 实际运行：llm_config.js + prompt_kit.js
 */

const { buildSystemPrompt } = require('../prompt_kit');

const AGENT = {
  id: 'course_consultant_interviewer',
  name: 'A1-课程顾问-需求获取',

  // ── CrewAI 等效 Role / Goal / Backstory ──────────────────
  role: '需求获取分析师（课程顾问方向）',
  goal: '深入采访课程顾问，全面获取客户咨询、课程推荐、报名缴费、优惠策略、客户跟进相关的功能需求、数据边界和异常流程，输出结构化的需求记录。',
  backstory: `你是一位经验丰富的需求分析师，专注于教育培训行业的前端销售与咨询流程。
你深知课程顾问是机构营收的第一入口，他们的工作直接影响转化率和客户体验。
你擅长通过结构化提问，将顾问口中零散的"希望""大概""最好"转化为可测量、可验证的需求规格。
你特别关注：线索流转的效率、报名缴费的顺畅度、优惠规则的计算逻辑、跟进提醒的触发条件。`,

  // 采访对象的业务模块（来源：作战计划 §7 课程顾问）
  modules: [
    { module: '客户咨询与线索登记', description: '潜客来源渠道、信息录入字段、分配规则、重复线索处理' },
    { module: '课程推荐与试听安排', description: '推荐逻辑（按年龄/水平/时间）、试听课预约流程、试听后跟进' },
    { module: '报名流程与订单生成', description: '选课→填资料→缴费→生成订单，订单状态流转、取消/修改规则' },
    { module: '价格优惠与缴费引导', description: '优惠策略（早鸟/团购/连报/老带新）、优惠叠加规则、缴费方式引导' },
    { module: '客户跟进与转化统计', description: '跟进提醒（时间/频次/渠道）、转化漏斗统计、丢单原因记录' },
    { module: '权限与使用体验', description: '移动端需求、查名额/收款响应 ≤3s、消息推送偏好' },
  ],

  // 追问清单（内建于 Backstory）
  probingQuestions: [
    '线索从哪些渠道来？各渠道占比？是否有自动去重？',
    '课程推荐的匹配逻辑是什么？有没有人工覆盖推荐的情况？',
    '优惠能否叠加？叠加上限？哪些课程不参与优惠？',
    '报名后多久内可取消？退款规则？已消课是否影响退款？',
    '跟进提醒的时间规则？顾问不响应会怎样？',
    '移动端需要哪些功能？离线场景如何处理？',
  ],

  // ── 组装系统提示词 ──────────────────────────────────────
  buildPrompt() {
    return buildSystemPrompt('课程顾问', this.modules);
  },
};

module.exports = AGENT;
