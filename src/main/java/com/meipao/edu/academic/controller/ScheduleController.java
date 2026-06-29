package com.meipao.edu.academic.controller;

import com.meipao.edu.core.model.dto.ApiResponse;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/academic")
public class ScheduleController {

    @GetMapping("/schedules")
    public ApiResponse<String> list(@RequestParam(required = false) Long classId) {
        return ApiResponse.success("schedules");
    }

    @PostMapping("/schedules")
    public ApiResponse<String> create() {
        return ApiResponse.success("schedule_created");
    }

    @PostMapping("/schedules/{scheduleId}/reschedule")
    public ApiResponse<String> reschedule(@PathVariable Long scheduleId) {
        return ApiResponse.success("reschedule_created");
    }
}
