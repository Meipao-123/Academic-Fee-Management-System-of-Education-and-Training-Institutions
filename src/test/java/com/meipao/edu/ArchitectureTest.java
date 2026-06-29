package com.meipao.edu;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.*;

/**
 * 架构约束自动验证 — DTS-EDU-V1 §5 / C-MOD-0001。
 * CI 中每次 PR 运行此测试，违规阻断合并。
 */
class ArchitectureTest {

    private static JavaClasses classes;

    @BeforeAll
    static void setUp() {
        classes = new ClassFileImporter().importPackages("com.meipao.edu");
    }

    @Test void core_no_biz_dep() {
        ArchRule rule = classes().that().resideInAPackage("..core..")
                .should().onlyDependOnClassesThat()
                .resideInAnyPackage("..core..", "java..", "jakarta..", "org.springframework..",
                        "lombok..", "com.fasterxml..", "io.jsonwebtoken..", "org.slf4j..", "org.aspectj..");
        rule.check(classes);
    }

    @Test void no_cycles() {
        slices().matching("com.meipao.edu.(*)..").should().beFreeOfCycles().check(classes);
    }

    @Test void controller_no_repository() {
        noClasses().that().resideInAPackage("..controller..")
                .should().dependOnClassesThat().resideInAPackage("..repository..")
                .check(classes);
    }

    @Test void report_no_entity_write() {
        noClasses().that().resideInAPackage("..report..")
                .should().dependOnClassesThat().resideInAPackage("jakarta.persistence..")
                .check(classes);
    }
}
