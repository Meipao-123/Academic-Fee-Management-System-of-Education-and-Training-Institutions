package com.meipao.edu.admin.model.entity;

import com.meipao.edu.core.model.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity @Table(name = "t_adm_user")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class User extends BaseEntity {
    @Column(nullable = false, unique = true, length = 50) private String username;
    @Column(nullable = false, length = 200) private String passwordHash;
    @Column(nullable = false, length = 30) private String role;
    @Column(length = 20) private String status = "ACTIVE";
}
