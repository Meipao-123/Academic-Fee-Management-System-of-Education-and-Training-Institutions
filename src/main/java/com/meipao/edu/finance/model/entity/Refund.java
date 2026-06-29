package com.meipao.edu.finance.model.entity;

import com.meipao.edu.core.model.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

@Entity @Table(name = "t_fin_refund")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Refund extends BaseEntity {
    @Column(nullable = false) private Long orderId;
    @Column(nullable = false) private Long studentId;
    @Column(nullable = false) private BigDecimal requestAmount;
    @Column(nullable = false) private BigDecimal calculatedAmount;
    private BigDecimal approvedAmount;
    @Column(length = 500) private String reason;
    @Enumerated(EnumType.STRING) private RefundStatus status = RefundStatus.APPLIED;
    public enum RefundStatus { APPLIED, SUPERVISOR, FINANCE, PRINCIPAL, APPROVED, REJECTED, PROCESSING, COMPLETED }
}
