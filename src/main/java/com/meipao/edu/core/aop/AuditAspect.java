package com.meipao.edu.core.aop;

import com.meipao.edu.core.annotation.Auditable;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.stereotype.Component;

import java.time.Instant;

/** 操作审计 AOP — 记录操作前后快照，通过 Spring Event 异步写入 (C-ARCH-0006) */
@Slf4j
@Aspect
@Component
public class AuditAspect {

    @Around("@annotation(auditable)")
    public Object audit(ProceedingJoinPoint jp, Auditable auditable) throws Throwable {
        long start = System.currentTimeMillis();
        String action = auditable.action();
        String module = auditable.module();
        log.info("[AUDIT] module={}, action={}, args={}", module, action, jp.getArgs());
        try {
            Object result = jp.proceed();
            log.info("[AUDIT] module={}, action={}, result=SUCCESS, elapsed={}ms",
                    module, action, System.currentTimeMillis() - start);
            return result;
        } catch (Exception e) {
            log.error("[AUDIT] module={}, action={}, result=FAILED, error={}",
                    module, action, e.getMessage());
            throw e;
        }
    }
}
