package com.meipao.edu.core.exception;

import lombok.Getter;

/**
 * 业务异常 — ADR-002 决策2 + C-CODE-0002。
 * 抛出后由 GlobalExceptionHandler 统一封装为 ApiResponse。
 */
@Getter
public class BusinessException extends RuntimeException {

    private final int errorCode;

    public BusinessException(int errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode.getCode();
    }

    public BusinessException(ErrorCode errorCode, String detail) {
        super(errorCode.getMessage() + ": " + detail);
        this.errorCode = errorCode.getCode();
    }
}
