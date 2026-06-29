package com.meipao.edu.crm.model.entity;

import com.meipao.edu.core.annotation.Encrypted;
import com.meipao.edu.core.annotation.Masked;
import com.meipao.edu.core.model.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "t_crm_student")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Student extends BaseEntity {

    @Column(nullable = false, length = 50)
    private String name;

    @Encrypted
    @Masked
    @Column(nullable = false, length = 20)
    private String phone;

    @Encrypted
    @Column(length = 50)
    private String wechatId;

    @Column(length = 10)
    private String ageGroup;

    @Enumerated(EnumType.STRING)
    private StudentStatus status = StudentStatus.ACTIVE;

    private Long leadId;
    private Long consultantId;

    public enum StudentStatus { ACTIVE, SUSPENDED, GRADUATED, LOST }
}
