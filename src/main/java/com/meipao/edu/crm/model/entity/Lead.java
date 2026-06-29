package com.meipao.edu.crm.model.entity;

import com.meipao.edu.core.model.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "t_crm_lead")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Lead extends BaseEntity {

    @Column(nullable = false, length = 50)
    private String name;

    @Column(nullable = false, length = 20)
    private String phone;

    @Column(nullable = false, length = 20)
    @Enumerated(EnumType.STRING)
    private LeadSource source;

    @Column(nullable = false, length = 20)
    @Enumerated(EnumType.STRING)
    private LeadStatus status = LeadStatus.PENDING;

    private Long consultantId;

    public enum LeadSource { ONLINE_AD, REFERRAL, WALK_IN, GROUND_PUSH }
    public enum LeadStatus { PENDING, FOLLOWING, CONVERTED, LOST }
}
