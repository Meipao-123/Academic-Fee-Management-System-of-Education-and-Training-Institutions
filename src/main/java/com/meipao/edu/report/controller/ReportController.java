package com.meipao.edu.report.controller;

import com.meipao.edu.core.model.dto.ApiResponse;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/report")
public class ReportController {

    @GetMapping("/dashboard")
    public ApiResponse<String> dashboard(@RequestParam(defaultValue = "TODAY") String dateRange) {
        return ApiResponse.success("dashboard_data");
    }

    @GetMapping("/funnels")
    public ApiResponse<String> funnels() { return ApiResponse.success("funnel_data"); }

    @GetMapping("/revenue")
    public ApiResponse<String> revenue() { return ApiResponse.success("revenue_data"); }
}
