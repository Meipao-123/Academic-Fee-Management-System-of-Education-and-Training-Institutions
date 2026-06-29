-- =============================================================================
-- Flyway V1: EDU 培训机构教务收费管理系统 — 基线 DDL
-- 对应: SRS-v1.2 §3.3.1 逻辑数据模型 / MDS-EDU-V1 7 模块
-- 约束: 软删除(deleted) / campus_id 隔离 / 审计日志不可变
-- =============================================================================

-- ── CRM: 线索与学员管理 ──
CREATE TABLE t_crm_lead (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    source VARCHAR(20) NOT NULL COMMENT 'ONLINE_AD/REFERRAL/WALK_IN/GROUND_PUSH',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/FOLLOWING/CONVERTED/LOST',
    consultant_id BIGINT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_lead_campus (campus_id),
    INDEX idx_lead_phone (phone),
    INDEX idx_lead_status (status)
);

CREATE TABLE t_crm_student (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    wechat_id VARCHAR(50),
    age_group VARCHAR(10),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE/SUSPENDED/GRADUATED/LOST',
    lead_id BIGINT,
    consultant_id BIGINT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE INDEX idx_student_phone (phone),
    INDEX idx_student_campus (campus_id),
    INDEX idx_student_consultant (consultant_id)
);

CREATE TABLE t_crm_follow_up (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    lead_id BIGINT NOT NULL,
    consultant_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    follow_up_time DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_follow_up_lead (lead_id)
);

CREATE TABLE t_crm_referral (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    referrer_student_id BIGINT NOT NULL COMMENT '推荐人学员ID',
    referred_student_id BIGINT NOT NULL COMMENT '被推荐学员ID',
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_referral_referrer (referrer_student_id)
);

-- ── ENR: 报名缴费与订单管理 ──
CREATE TABLE t_enr_course (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(30) NOT NULL COMMENT 'FIXED_HOURS/TERM/STAGE',
    unit_price DECIMAL(10,2),
    total_hours INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_course_campus (campus_id)
);

CREATE TABLE t_enr_class (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    course_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    teacher_id BIGINT,
    room VARCHAR(50),
    max_capacity INT NOT NULL,
    occupied_count INT NOT NULL DEFAULT 0,
    semester_start DATE,
    semester_end DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_class_course (course_id),
    INDEX idx_class_campus (campus_id)
);

CREATE TABLE t_enr_order (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    order_no VARCHAR(32) NOT NULL,
    student_id BIGINT NOT NULL,
    class_id BIGINT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/PAID/CANCELLED/REFUNDED',
    promotion_code VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE INDEX idx_order_no (order_no),
    INDEX idx_order_student (student_id),
    INDEX idx_order_campus (campus_id)
);

CREATE TABLE t_enr_payment (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    channel VARCHAR(20) NOT NULL COMMENT 'WECHAT/ALIPAY/BANK_TRANSFER',
    transaction_no VARCHAR(64),
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/CONFIRMED/ABNORMAL/UNCLAIMED/REFUNDED',
    match_label VARCHAR(20) COMMENT 'EXACT/FUZZY/MANUAL',
    paid_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_payment_order (order_id),
    INDEX idx_payment_transaction (transaction_no)
);

-- ── ACA: 教务排课与消课管理 ──
CREATE TABLE t_aca_schedule (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    class_id BIGINT NOT NULL,
    teacher_id BIGINT NOT NULL,
    room_id BIGINT,
    weekday INT NOT NULL COMMENT '1=Mon, 7=Sun',
    time_start TIME NOT NULL,
    time_end TIME NOT NULL,
    semester_start DATE NOT NULL,
    semester_end DATE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_schedule_class (class_id),
    INDEX idx_schedule_teacher (teacher_id),
    INDEX idx_schedule_campus (campus_id)
);

CREATE TABLE t_aca_lesson (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    schedule_id BIGINT NOT NULL,
    lesson_date DATE NOT NULL,
    time_start TIME NOT NULL,
    time_end TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED' COMMENT 'SCHEDULED/COMPLETED/CANCELLED',
    INDEX idx_lesson_schedule (schedule_id),
    INDEX idx_lesson_date (lesson_date)
);

CREATE TABLE t_aca_attendance (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    lesson_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL COMMENT 'PRESENT/LATE/ABSENT/LEAVE',
    method VARCHAR(20) COMMENT 'QR_SCAN/MANUAL',
    hour_type VARCHAR(20) NOT NULL DEFAULT 'NORMAL' COMMENT 'NORMAL/GIFT/MAKEUP',
    check_in_time DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_attendance_unique (student_id, lesson_id),
    INDEX idx_attendance_lesson (lesson_id)
);

CREATE TABLE t_aca_reschedule (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    schedule_id BIGINT NOT NULL,
    new_date DATE NOT NULL,
    new_time_start TIME NOT NULL,
    new_time_end TIME NOT NULL,
    reason VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/AGREED/REJECTED/TIMEOUT/COORDINATING/CANCELLED',
    deadline DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_reschedule_schedule (schedule_id)
);

CREATE TABLE t_aca_leave (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    lesson_id BIGINT,
    reason VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/APPROVED/REJECTED',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_leave_student (student_id)
);

-- ── FIN: 财务管理与核算 ──
CREATE TABLE t_fin_ledger (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    entry_type VARCHAR(20) NOT NULL COMMENT 'PAYMENT/REFUND/ADJUSTMENT',
    amount DECIMAL(10,2) NOT NULL,
    balance_after DECIMAL(10,2),
    summary VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ledger_order (order_id),
    INDEX idx_ledger_campus (campus_id)
);

CREATE TABLE t_fin_refund (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    request_amount DECIMAL(10,2) NOT NULL,
    calculated_amount DECIMAL(10,2) NOT NULL,
    approved_amount DECIMAL(10,2),
    reason VARCHAR(500),
    status VARCHAR(30) NOT NULL DEFAULT 'APPLIED' COMMENT 'APPLIED/SUPERVISOR/FINANCE/PRINCIPAL/APPROVED/REJECTED/PROCESSING/COMPLETED',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_refund_order (order_id),
    INDEX idx_refund_status (status)
);

-- ── RPT: 只读，无独立表（查询其他模块表） ──

-- ── ADM: 系统管理与基础配置 ──
CREATE TABLE t_adm_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(30) NOT NULL COMMENT 'CONSULTANT/ACADEMIC/FINANCE/PRINCIPAL/ADMIN',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE INDEX idx_user_username (username)
);

CREATE TABLE t_adm_audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campus_id BIGINT,
    operator_id BIGINT,
    operator_name VARCHAR(50),
    module VARCHAR(30),
    action VARCHAR(50),
    target_type VARCHAR(50),
    target_id VARCHAR(50),
    before_snapshot TEXT,
    after_snapshot TEXT,
    ip_address VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_created (created_at),
    INDEX idx_audit_module (module)
) COMMENT '审计日志 — 不可修改、不可删除 (NFR-AUD-002)';

CREATE TABLE t_adm_system_config (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL,
    config_value TEXT,
    description VARCHAR(500),
    updated_by VARCHAR(50),
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_config_key (config_key)
);
