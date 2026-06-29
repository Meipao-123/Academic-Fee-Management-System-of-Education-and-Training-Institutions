package com.meipao.edu.enrollment.controller;

import com.meipao.edu.core.model.dto.ApiResponse;
import com.meipao.edu.enrollment.model.entity.EnrollmentOrder;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/enrollment/orders")
public class OrderController {

    @PostMapping
    public ApiResponse<String> create(@Valid @RequestBody CreateOrderRequest req) {
        // TODO: 委托 EnrollmentService.createOrder
        return ApiResponse.success("ORD-" + System.currentTimeMillis());
    }

    @GetMapping("/{orderId}")
    public ApiResponse<String> get(@PathVariable String orderId) {
        return ApiResponse.success("order:" + orderId);
    }

    @PostMapping("/{orderId}/payment")
    public ApiResponse<String> pay(@PathVariable String orderId,
                                   @Valid @RequestBody PayRequest req) {
        return ApiResponse.success("payment_initiated");
    }

    @PostMapping("/{orderId}/cancel")
    public ApiResponse<String> cancel(@PathVariable String orderId) {
        return ApiResponse.success("cancelled");
    }

    public record CreateOrderRequest(@NotNull Long studentId, @NotNull Long classId, String couponCode) {}
    public record PayRequest(@NotNull String channel) {}
}
