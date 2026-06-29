package com.meipao.edu;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * EDU 培训机构教务收费管理系统 — 模块化分层单体应用入口。
 *
 * <p>架构: Controller → Service → Repository → Model 四层分层
 * <p>模块: edu.core / edu.crm / edu.enrollment / edu.academic / edu.finance / edu.report / edu.admin
 */
@SpringBootApplication
@EnableAsync
@EnableCaching
public class EduApplication {

    public static void main(String[] args) {
        SpringApplication.run(EduApplication.class, args);
    }
}
