package com.example.backend.dto;

import java.util.List;
//this is the one which return the python code to the frontend
public class AnalyzeResponseDTO {

    private Long studentId;
    private String questionId;

    private QuestionAnalysisDTO question_analysis;
    private CodeAnalysisDTO code_analysis;
    private TestSummaryDTO test_summary;
    private List<TestResultDTO> test_results;
    private List<LogicalErrorDTO> logical_errors;
    private List<ViolationDTO> violations;
    public List<ViolationDTO> getViolations() {
        return violations;
    }

    public void setViolations(List<ViolationDTO> violations) {
        this.violations = violations;
    }

    private Integer error_count;
    private boolean has_logical_errors;

    // ===== GETTERS & SETTERS =====

    public Long getStudentId() {
        return studentId;
    }

    public void setStudentId(Long studentId) {
        this.studentId = studentId;
    }

    public String getQuestionId() {
        return questionId;
    }

    public void setQuestionId(String questionId) {
        this.questionId = questionId;
    }

    public QuestionAnalysisDTO getQuestion_analysis() {
        return question_analysis;
    }

    public void setQuestion_analysis(QuestionAnalysisDTO question_analysis) {
        this.question_analysis = question_analysis;
    }

    public CodeAnalysisDTO getCode_analysis() {
        return code_analysis;
    }

    public void setCode_analysis(CodeAnalysisDTO code_analysis) {
        this.code_analysis = code_analysis;
    }

    public TestSummaryDTO getTest_summary() {
        return test_summary;
    }

    public void setTest_summary(TestSummaryDTO test_summary) {
        this.test_summary = test_summary;
    }

    public List<TestResultDTO> getTest_results() {
        return test_results;
    }

    public void setTest_results(List<TestResultDTO> test_results) {
        this.test_results = test_results;
    }

    public List<LogicalErrorDTO> getLogical_errors() {
        return logical_errors;
    }

    public void setLogical_errors(List<LogicalErrorDTO> logical_errors) {
        this.logical_errors = logical_errors;
    }

    public Integer getError_count() {
        return error_count;
    }

    public void setError_count(Integer error_count) {
        this.error_count = error_count;
    }

    public boolean isHas_logical_errors() {
        return has_logical_errors;
    }

    public void setHas_logical_errors(boolean has_logical_errors) {
        this.has_logical_errors = has_logical_errors;
    }
}