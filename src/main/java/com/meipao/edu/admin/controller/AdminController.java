package com.meipao.edu.admin.controller;

import com.meipao.edu.core.model.dto.ApiResponse;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/admin")
public class AdminController {

    @GetMapping("/users")
    public ApiResponse<String> listUsers() { return ApiResponse.success("users"); }

    @PostMapping("/users")
    public ApiResponse<String> createUser() { return ApiResponse.success("user_created"); }

    @PutMapping("/configs")
    public ApiResponse<String> updateConfig() { return ApiResponse.success("config_updated"); }

    @GetMapping("/audit-logs")
    public ApiResponse<String> auditLogs() { return ApiResponse.success("audit_logs"); }
}
