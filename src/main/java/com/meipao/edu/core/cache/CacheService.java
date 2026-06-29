package com.meipao.edu.core.cache;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.Optional;
import java.util.concurrent.ThreadLocalRandom;
import java.util.function.Supplier;

/**
 * 缓存统一入口 — Cache-Aside 模式 + 互斥锁防击穿 (ADR-004 / C-CODE-0004)。
 * 禁止直接使用 RedisTemplate 或 @Cacheable。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CacheService {

    private final RedisTemplate<String, Object> redisTemplate;

    /** 空值标记 — 防止缓存穿透 (ADR-004 决策4) */
    private static final String NULL_PLACEHOLDER = "__null__";

    @SuppressWarnings("unchecked")
    public <T> T getOrLoad(String key, Class<T> type, Supplier<T> loader, Duration baseTtl) {
        Object cached = redisTemplate.opsForValue().get(key);
        if (cached != null) {
            if (NULL_PLACEHOLDER.equals(cached)) return null;
            return (T) cached;
        }
        // 互斥锁防击穿
        String lockKey = "lock:" + key;
        Boolean locked = redisTemplate.opsForValue().setIfAbsent(lockKey, "1", Duration.ofSeconds(5));
        if (Boolean.TRUE.equals(locked)) {
            try {
                T value = loader.get();
                if (value != null) {
                    redisTemplate.opsForValue().set(key, value, baseTtl);
                } else {
                    redisTemplate.opsForValue().set(key, NULL_PLACEHOLDER, Duration.ofMinutes(1));
                }
                return value;
            } finally {
                redisTemplate.delete(lockKey);
            }
        }
        // 未获锁，等待后重试
        try { Thread.sleep(100); } catch (InterruptedException ignored) {}
        Object retry = redisTemplate.opsForValue().get(key);
        return retry != null && !NULL_PLACEHOLDER.equals(retry) ? (T) retry : null;
    }

    public void set(String key, Object value, Duration ttl) {
        redisTemplate.opsForValue().set(key, value, ttl);
    }

    public void delete(String key) {
        redisTemplate.delete(key);
    }

    public Duration randomizeTtl(Duration base) {
        long ms = base.toMillis();
        long jitter = (long)(ms * 0.2 * ThreadLocalRandom.current().nextDouble() * (ThreadLocalRandom.current().nextBoolean() ? 1 : -1));
        return Duration.ofMillis(Math.max(ms + jitter, 1000));
    }
}
