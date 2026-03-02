package com.example.backend.dto;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class EvaluationRequestDTO {

    private Long studentId;
    @JsonProperty("question_id")
    private String questionId;
     private boolean passed;
    public boolean isPassed() {
        return passed;
    }

     public void setPassed(boolean passed) {
         this.passed = passed;
     }

    @JsonProperty("problem_statement")
    private String problemStatement;
      @JsonProperty("runtime_output")
    private String runtimeOutput;

    @JsonProperty("runtime_error")
    private String runtimeError;

    private String code;

    @JsonProperty("test_cases")
    private List<PythonTestCaseDTO> testCases;

    private String language;

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

    public String getProblemStatement() {
        return problemStatement;
    }

    public void setProblemStatement(String problemStatement) {
        this.problemStatement = problemStatement;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public List<PythonTestCaseDTO> getTestCases() {
        return testCases;
    }

    public void setTestCases(List<PythonTestCaseDTO> testCases) {
        this.testCases = testCases;
    }

    public String getLanguage() {
        return language;
    }

    public void setLanguage(String language) {
        this.language = language;
    }

    public String getRuntimeOutput() {
        return runtimeOutput;
    }

    public void setRuntimeOutput(String runtimeOutput) {
        this.runtimeOutput = runtimeOutput;
    }

    public String getRuntimeError() {
        return runtimeError;
    }

    public void setRuntimeError(String runtimeError) {
        this.runtimeError = runtimeError;
    }
 
    // getters and setters
    
}