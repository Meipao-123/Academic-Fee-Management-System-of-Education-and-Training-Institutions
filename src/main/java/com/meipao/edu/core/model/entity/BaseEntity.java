package com.meipao.edu.core.model.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import org.hibernate.annotations.SoftDelete;

import java.time.LocalDateTime;

/**
 * JPA 实体基类，提供统一字段: id / campusId / createdAt / updatedAt / deleted。
 * 所有业务实体的 Repository 基类自动注入 campus_id 过滤。
 */
@Getter
@Setter
@MappedSuperclass
public abstract class BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 校区 ID — 数据隔离核心字段。Repository 基类强制注入 WHERE campus_id = ? */
    @Column(name = "campus_id", nullable = false)
    private Long campusId;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    /** 软删除标记 — NFR-AUD-003: 核心业务数据仅软删除 */
    @Column(name = "deleted")
    private Boolean deleted = false;
}
