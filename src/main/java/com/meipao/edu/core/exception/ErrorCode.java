package com.meipao.edu.core.exception;

import lombok.Getter;

/**
 * 6 位错误码枚举 — ADR-002 决策4 + C-CODE-0003。
 * 格式: {模块2位}{类别2位}{序号2位}
 * 模块: 00=CORE, 01=CRM, 02=ENR, 03=ACA, 04=FIN, 05=RPT, 06=ADM
 * 类别: 01=参数校验, 02=业务规则, 03=权限, 04=外部调用, 05=数据
 */
@Getter
public enum ErrorCode {

    // ── CORE (00) ──
    UNKNOWN(999999, "未知系统异常"),
    VALIDATION_ERROR(1, "参数校验失败"),
    UNAUTHORIZED(3, "未认证或 Token 已过期"),
    FORBIDDEN(3003, "权限不足"),
    RATE_LIMITED(3004, "请求过于频繁，请稍后再试"),

    // ── CRM (01) ──
    CRM_DUPLICATE_PHONE(10102, "手机号已被其他学员使用"),
    CRM_LEAD_NOT_FOUND(10201, "线索不存在"),

    // ── ENR (02) ──
    ENR_ORDER_NOT_FOUND(20201, "订单不存在"),
    ENR_ORDER_CANNOT_CANCEL(20202, "订单当前状态不可取消"),
    ENR_PAYMENT_TIMEOUT(20401, "支付网关响应超时"),

    // ── ACA (03) ──
    ACA_SCHEDULE_CONFLICT(30201, "排课时间段冲突"),
    ACA_CLASS_FULL(30202, "班级名额已满"),
    ACA_RESCHEDULE_TIMEOUT(30203, "调课确认已超时"),

    // ── FIN (04) ──
    FIN_REFUND_NOT_FOUND(40201, "退费申请不存在"),
    FIN_REFUND_APPROVAL_DENIED(40202, "退费审批不通过"),
    FIN_RECONCILIATION_MISMATCH(40401, "银行流水与订单金额不匹配"),

    // ── RPT (05) ──
    RPT_QUERY_TIMEOUT(50201, "报表查询超时，请缩小查询范围"),

    // ── ADM (06) ──
    ADM_USER_NOT_FOUND(60201, "用户不存在"),
    ADM_CONFIG_KEY_NOT_FOUND(60202, "配置项不存在");

    private final int code;
    private final String message;

    ErrorCode(int code, String message) {
        this.code = code;
        this.message = message;
    }
}
