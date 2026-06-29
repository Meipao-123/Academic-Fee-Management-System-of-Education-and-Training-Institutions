package com.meipao.edu.crm.service;

import com.meipao.edu.crm.model.entity.Lead;

import java.util.List;

/** 线索管理服务接口 — MDS MOD-001 / C-MOD-0002: 对外仅暴露 interface */
public interface LeadService {
    Lead createLead(Long campusId, String name, String phone, Lead.LeadSource source);
    List<Lead> listLeads(Lead.LeadStatus status, int page, int size);
    Lead convertToStudent(Long leadId, Long consultantId);
}
