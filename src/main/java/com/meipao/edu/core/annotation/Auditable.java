package com.meipao.edu.core.annotation;

import java.lang.annotation.*;

@Target(ElementType.METHOD) @Retention(RetentionPolicy.RUNTIME)
public @interface Auditable {
    String action();
    String module();
}
