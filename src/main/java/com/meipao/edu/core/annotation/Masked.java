package com.meipao.edu.core.annotation;

import java.lang.annotation.*;

@Target(ElementType.FIELD) @Retention(RetentionPolicy.RUNTIME)
public @interface Masked {
    MaskType value() default MaskType.PHONE;
    enum MaskType { PHONE, ID_CARD, NAME }
}
