package com.meipao.edu.crm.repository;

import com.meipao.edu.crm.model.entity.Lead;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface LeadRepository extends JpaRepository<Lead, Long>, JpaSpecificationExecutor<Lead> {
    Optional<Lead> findByPhoneAndDeletedFalse(String phone);
    List<Lead> findByStatusAndDeletedFalse(Lead.LeadStatus status);
}
