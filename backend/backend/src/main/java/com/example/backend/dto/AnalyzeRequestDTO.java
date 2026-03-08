package com.example.backend.dto;

import java.util.List;
import com.example.backend.dto.*;
import com.fasterxml.jackson.annotation.JsonProperty;
//gets data from the frontend
public class AnalyzeRequestDTO {

    private Long studentId;
    private String questionId;
    private String code;
    private String language;

    @JsonProperty("problem_statement")
    private String problemStatement;

    @JsonProperty("test_cases")
    private List<TestCaseDTO> testCases;

    public Long getStudentId() {
        return studentId;
    }

    public void setStudentId(Long studentId) {
        this.studentId = studentId;
    }

    public String
    
    getQuestionId() {
        return questionId;
    }

    public void setQuestionId(String questionId) {
        this.questionId = questionId;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getLanguage() {
        return language;
    }

    public void setLanguage(String language) {
        this.language = language;
    }

    public String getProblemStatement() {
        return problemStatement;
    }

    public void setProblemStatement(String problemStatement) {
        this.problemStatement = problemStatement;
    }

    public List<TestCaseDTO> getTestCases() {
        return testCases;
    }

    public void setTestCases(List<TestCaseDTO> testCases) {
        this.testCases = testCases;
    }

    
}