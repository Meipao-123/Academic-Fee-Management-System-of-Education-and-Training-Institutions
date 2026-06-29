package com.meipao.edu.crm.controller;

import com.meipao.edu.core.model.dto.ApiResponse;
import com.meipao.edu.crm.model.entity.Lead;
import com.meipao.edu.crm.service.LeadService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/crm/leads")
@RequiredArgsConstructor
public class LeadController {

    private final LeadService leadService;

    @PostMapping
    public ApiResponse<Lead> create(@Valid @RequestBody CreateLeadRequest req) {
        return ApiResponse.success(leadService.createLead(req.campusId, req.name, req.phone, req.source));
    }

    @GetMapping
    public ApiResponse<java.util.List<Lead>> list(
            @RequestParam(required = false) Lead.LeadStatus status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.success(leadService.listLeads(status, page, size));
    }

    @PostMapping("/{leadId}/convert")
    public ApiResponse<Lead> convert(@PathVariable Long leadId,
                                     @RequestParam Long consultantId) {
        return ApiResponse.success(leadService.convertToStudent(leadId, consultantId));
    }

    public record CreateLeadRequest(
            @NotBlank String name,
            @NotBlank String phone,
            @NotNull Lead.LeadSource source,
            @NotNull Long campusId) {}
}
