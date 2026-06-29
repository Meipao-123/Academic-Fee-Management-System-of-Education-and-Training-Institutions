package com.meipao.edu.enrollment.model.entity;

import com.meipao.edu.core.model.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity @Table(name = "t_enr_payment")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Payment extends BaseEntity {
    @Column(nullable = false) private Long orderId;
    @Column(nullable = false, length = 20) @Enumerated(EnumType.STRING) private PaymentChannel channel;
    @Column(length = 64) private String transactionNo;
    @Column(nullable = false) private BigDecimal amount;
    @Enumerated(EnumType.STRING) private PaymentStatus status = PaymentStatus.PENDING;
    @Column(length = 20) private String matchLabel;
    private LocalDateTime paidAt;
    public enum PaymentChannel { WECHAT, ALIPAY, BANK_TRANSFER }
    public enum PaymentStatus { PENDING, CONFIRMED, ABNORMAL, UNCLAIMED, REFUNDED }
}
