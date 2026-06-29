package com.meipao.edu.enrollment.model.entity;

import com.meipao.edu.core.model.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity @Table(name = "t_enr_order")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class EnrollmentOrder extends BaseEntity {
    @Column(nullable = false, unique = true, length = 32) private String orderNo;
    @Column(nullable = false) private Long studentId;
    @Column(nullable = false) private Long classId;
    @Column(nullable = false) private java.math.BigDecimal totalAmount;
    private java.math.BigDecimal discountAmount = java.math.BigDecimal.ZERO;
    private java.math.BigDecimal paidAmount = java.math.BigDecimal.ZERO;
    @Enumerated(EnumType.STRING) private OrderStatus status = OrderStatus.PENDING;
    private String promotionCode;
    public enum OrderStatus { PENDING, PAID, CANCELLED, REFUNDED }
}
