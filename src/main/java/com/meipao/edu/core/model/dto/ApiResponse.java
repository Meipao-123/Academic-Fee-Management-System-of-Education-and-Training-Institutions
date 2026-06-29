package com.meipao.edu.core.model.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * 统一 API 响应体 — ADR-002 决策3。
 * <pre>{@code
 * { "code": 0, "message": "success", "data": {...}, "timestamp": "...", "traceId": "..." }
 * }</pre>
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {

    /** 0=成功, 1xxxxx=业务异常, 9xxxxx=系统异常 */
    private int code;

    private String message;

    private T data;

    @Builder.Default
    private Instant timestamp = Instant.now();

    /** 全链路追踪 ID（MDC 注入） */
    private String traceId;

    // ── 工厂方法 ──

    public static <T> ApiResponse<T> success(T data) {
        return ApiResponse.<T>builder()
                .code(0).message("success").data(data)
                .timestamp(Instant.now()).traceId(currentTraceId())
                .build();
    }

    public static <T> ApiResponse<T> error(int code, String message) {
        return ApiResponse.<T>builder()
                .code(code).message(message).data(null)
                .timestamp(Instant.now()).traceId(currentTraceId())
                .build();
    }

    private static String currentTraceId() {
        return org.slf4j.MDC.get("traceId");
    }
}
