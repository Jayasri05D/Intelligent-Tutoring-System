// package com.example.backend.entity;

// import java.time.LocalDateTime;

// import jakarta.persistence.Column;
// import jakarta.persistence.GeneratedValue;
// import jakarta.persistence.GenerationType;
// import jakarta.persistence.JoinColumn;
// import jakarta.persistence.ManyToOne;
// import jakarta.persistence.OneToMany;

// import jakarta.persistence.*;
// import java.util.List;

// @Entity
// @Table(name = "submissions")
// public class Submission {
//     @Id
//     @GeneratedValue(strategy = GenerationType.IDENTITY)
//     private Long id;

//     @Column(columnDefinition = "TEXT")
//     private String codeText;

//     private String language;

//     private boolean hasSyntaxError;

//     private LocalDateTime submittedAt = LocalDateTime.now();

//     @ManyToOne
//     @JoinColumn(name = "student_id")
//     private Student student;

//     @OneToMany(mappedBy = "submission", cascade = CascadeType.ALL)
//     private List<Misconception> misconceptions;

//     public Long getId() {
//         return id;
//     }

//     public void setId(Long id) {
//         this.id = id;
//     }

//     public String getCodeText() {
//         return codeText;
//     }

//     public void setCodeText(String codeText) {
//         this.codeText = codeText;
//     }

//     public String getLanguage() {
//         return language;
//     }

//     public void setLanguage(String language) {
//         this.language = language;
//     }

//     public boolean isHasSyntaxError() {
//         return hasSyntaxError;
//     }

//     public void setHasSyntaxError(boolean hasSyntaxError) {
//         this.hasSyntaxError = hasSyntaxError;
//     }

//     public LocalDateTime getSubmittedAt() {
//         return submittedAt;
//     }

//     public void setSubmittedAt(LocalDateTime submittedAt) {
//         this.submittedAt = submittedAt;
//     }

//     public Student getStudent() {
//         return student;
//     }

//     public void setStudent(Student student) {
//         this.student = student;
//     }

//     public List<Misconception> getMisconceptions() {
//         return misconceptions;
//     }

//     public void setMisconceptions(List<Misconception> misconceptions) {
//         this.misconceptions = misconceptions;
//     }

    

// }
package com.example.backend.entity;

import java.time.LocalDateTime;
import java.util.List;
import jakarta.persistence.*;

@Entity
@Table(name = "submissions")
public class Submission {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(columnDefinition = "TEXT")
    private String codeText;

    private String language;

    private boolean hasSyntaxError;

    private boolean passed;   // ✅ NEW (test case result)

    @Column(columnDefinition = "TEXT")
    private String runtimeOutput;  // ✅ NEW

    @Column(columnDefinition = "TEXT")
    private String runtimeError;   // ✅ NEW

    private LocalDateTime submittedAt = LocalDateTime.now();

    // ===============================
    // 🔗 Relationships
    // ===============================

    @ManyToOne
    @JoinColumn(name = "student_id")
    private Student student;

    @ManyToOne                     // ✅ NEW
    @JoinColumn(name = "question_id")
    private Question question;

    @OneToMany(mappedBy = "submission", cascade = CascadeType.ALL)
    private List<Misconception> misconceptions;

    // ===============================
    // Getters and Setters
    // ===============================

    public Long getId() { return id; }

    public void setId(Long id) { this.id = id; }

    public String getCodeText() { return codeText; }

    public void setCodeText(String codeText) { this.codeText = codeText; }

    public String getLanguage() { return language; }

    public void setLanguage(String language) { this.language = language; }

    public boolean isHasSyntaxError() { return hasSyntaxError; }

    public void setHasSyntaxError(boolean hasSyntaxError) {
        this.hasSyntaxError = hasSyntaxError;
    }

    public boolean isPassed() { return passed; }

    public void setPassed(boolean passed) { this.passed = passed; }

    public String getRuntimeOutput() { return runtimeOutput; }

    public void setRuntimeOutput(String runtimeOutput) {
        this.runtimeOutput = runtimeOutput;
    }

    public String getRuntimeError() { return runtimeError; }

    public void setRuntimeError(String runtimeError) {
        this.runtimeError = runtimeError;
    }

    public LocalDateTime getSubmittedAt() { return submittedAt; }

    public void setSubmittedAt(LocalDateTime submittedAt) {
        this.submittedAt = submittedAt;
    }

    public Student getStudent() { return student; }

    public void setStudent(Student student) { this.student = student; }

    public Question getQuestion() { return question; }

    public void setQuestion(Question question) {
        this.question = question;
    }

    public List<Misconception> getMisconceptions() {
        return misconceptions;
    }

    public void setMisconceptions(List<Misconception> misconceptions) {
        this.misconceptions = misconceptions;
    }
}