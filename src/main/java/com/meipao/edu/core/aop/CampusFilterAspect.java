package com.meipao.edu.core.aop;

import io.jsonwebtoken.Claims;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

/**
 * 校区数据隔离 AOP — 从 JWT Claims 提取 campusId 写入 ThreadLocal,
 * Repository 基类读取并注入 WHERE campus_id = ? (C-ARCH-0004)
 */
@Slf4j
@Aspect
@Component
public class CampusFilterAspect {

    private static final ThreadLocal<Long> CURRENT_CAMPUS = new ThreadLocal<>();

    @Before("@within(com.meipao.edu.core.annotation.RequireCampus) || @annotation(com.meipao.edu.core.annotation.RequireCampus)")
    public void injectCampus(JoinPoint jp) {
        var auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.getDetails() instanceof Claims claims) {
            Long campusId = claims.get("campusId", Long.class);
            if (campusId != null) {
                CURRENT_CAMPUS.set(campusId);
                log.debug("CampusFilter: campus_id={} injected for {}", campusId, jp.getSignature().toShortString());
            }
        }
    }

    public static Long getCurrentCampus() { return CURRENT_CAMPUS.get(); }
    public static void clear() { CURRENT_CAMPUS.remove(); }
}
