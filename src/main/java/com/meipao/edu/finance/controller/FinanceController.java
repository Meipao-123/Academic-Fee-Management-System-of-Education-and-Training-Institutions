package com.meipao.edu.finance.controller;

import com.meipao.edu.core.model.dto.ApiResponse;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/finance")
public class FinanceController {

    @GetMapping("/ledgers")
    public ApiResponse<String> listLedgers() { return ApiResponse.success("ledgers"); }

    @PostMapping("/refunds")
    public ApiResponse<String> createRefund() { return ApiResponse.success("refund_created"); }

    @PostMapping("/refunds/{refundId}/approve")
    public ApiResponse<String> approveRefund(@PathVariable Long refundId) {
        return ApiResponse.success("refund_approved");
    }
}
