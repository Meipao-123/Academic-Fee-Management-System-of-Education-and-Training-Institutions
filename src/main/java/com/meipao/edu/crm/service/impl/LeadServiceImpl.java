package com.meipao.edu.crm.service.impl;

import com.meipao.edu.core.annotation.Auditable;
import com.meipao.edu.core.annotation.RequireCampus;
import com.meipao.edu.core.exception.BusinessException;
import com.meipao.edu.core.exception.ErrorCode;
import com.meipao.edu.crm.model.entity.Lead;
import com.meipao.edu.crm.model.entity.Student;
import com.meipao.edu.crm.repository.LeadRepository;
import com.meipao.edu.crm.repository.StudentRepository;
import com.meipao.edu.crm.service.LeadService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class LeadServiceImpl implements LeadService {

    private final LeadRepository leadRepository;
    private final StudentRepository studentRepository;

    @Override
    @RequireCampus
    @Transactional
    public Lead createLead(Long campusId, String name, String phone, Lead.LeadSource source) {
        leadRepository.findByPhoneAndDeletedFalse(phone).ifPresent(existing -> {
            throw new BusinessException(ErrorCode.CRM_DUPLICATE_PHONE);
        });
        Lead lead = Lead.builder()
                .campusId(campusId).name(name).phone(phone)
                .source(source).status(Lead.LeadStatus.PENDING).build();
        return leadRepository.save(lead);
    }

    @Override
    @RequireCampus
    public List<Lead> listLeads(Lead.LeadStatus status, int page, int size) {
        if (status != null) return leadRepository.findByStatusAndDeletedFalse(status);
        return leadRepository.findAll();
    }

    @Override
    @Auditable(action = "CONVERT_LEAD", module = "CRM")
    @Transactional
    public Lead convertToStudent(Long leadId, Long consultantId) {
        Lead lead = leadRepository.findById(leadId)
                .orElseThrow(() -> new BusinessException(ErrorCode.CRM_LEAD_NOT_FOUND));
        lead.setStatus(Lead.LeadStatus.CONVERTED);
        leadRepository.save(lead);

        Student student = Student.builder()
                .campusId(lead.getCampusId()).name(lead.getName())
                .phone(lead.getPhone()).leadId(leadId)
                .consultantId(consultantId).status(Student.StudentStatus.ACTIVE).build();
        studentRepository.save(student);
        log.info("线索转化: leadId={} -> studentId={}", leadId, student.getId());
        return lead;
    }
}
