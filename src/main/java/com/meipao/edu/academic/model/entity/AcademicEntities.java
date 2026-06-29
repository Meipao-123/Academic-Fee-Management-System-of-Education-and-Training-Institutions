package com.meipao.edu.academic.model.entity;

import com.meipao.edu.core.model.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.time.LocalTime;

@Entity @Table(name = "t_aca_schedule")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Schedule extends BaseEntity {
    @Column(nullable = false) private Long classId;
    @Column(nullable = false) private Long teacherId;
    private Long roomId;
    @Column(nullable = false) private Integer weekday;
    @Column(nullable = false) private LocalTime timeStart;
    @Column(nullable = false) private LocalTime timeEnd;
    @Column(nullable = false) private LocalDate semesterStart;
    @Column(nullable = false) private LocalDate semesterEnd;
}

@Entity @Table(name = "t_aca_attendance")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
class Attendance extends BaseEntity {
    @Column(nullable = false) private Long studentId;
    @Column(nullable = false) private Long lessonId;
    @Column(nullable = false, length = 20) @Enumerated(EnumType.STRING) private AttendanceStatus status;
    @Column(length = 20) private String method;
    @Column(length = 20) private String hourType = "NORMAL";
    private java.time.LocalDateTime checkInTime;
    public enum AttendanceStatus { PRESENT, LATE, ABSENT, LEAVE }
}

@Entity @Table(name = "t_aca_reschedule")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
class RescheduleRequest extends BaseEntity {
    @Column(nullable = false) private Long scheduleId;
    @Column(nullable = false) private LocalDate newDate;
    @Column(nullable = false) private LocalTime newTimeStart;
    @Column(nullable = false) private LocalTime newTimeEnd;
    @Column(length = 500) private String reason;
    @Enumerated(EnumType.STRING) private RescheduleStatus status = RescheduleStatus.PENDING;
    private java.time.LocalDateTime deadline;
    public enum RescheduleStatus { PENDING, AGREED, REJECTED, TIMEOUT, COORDINATING, CANCELLED }
}
