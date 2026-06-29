package com.meipao.edu.core.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.Map;

/** JWT 生成/验证 — Access Token 2h + Refresh Token 7d (ASD §5 / C-ARCH-0002) */
@Component
public class JwtProvider {

    private final SecretKey key;
    private final long accessTtl;
    private final long refreshTtl;

    public JwtProvider(@Value("${jwt.secret}") String secret,
                       @Value("${jwt.access-token-ttl}") long accessTtl,
                       @Value("${jwt.refresh-token-ttl}") long refreshTtl) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.accessTtl = accessTtl;
        this.refreshTtl = refreshTtl;
    }

    public String createAccessToken(Long userId, String username, String role, Long campusId) {
        return buildToken(userId, username, role, campusId, accessTtl);
    }

    public String createRefreshToken(Long userId, String username) {
        return buildToken(userId, username, null, null, refreshTtl);
    }

    public Claims parseToken(String token) {
        return Jwts.parser().verifyWith(key).build()
                .parseSignedClaims(token).getPayload();
    }

    public boolean validateToken(String token) {
        try { parseToken(token); return true; }
        catch (JwtException e) { return false; }
    }

    private String buildToken(Long userId, String username, String role, Long campusId, long ttl) {
        var now = new Date();
        var builder = Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("username", username)
                .issuedAt(now)
                .expiration(new Date(now.getTime() + ttl * 1000))
                .signWith(key);
        if (role != null) builder.claim("role", role);
        if (campusId != null) builder.claim("campusId", campusId);
        return builder.compact();
    }
}
