package com.example.backend.dto;

import java.util.List;
import com.fasterxml.jackson.annotation.JsonProperty;

public class PythonAnalyzeRequestDTO {

    private Long studentId;
    private String questionId;

    @JsonProperty("problem_statement")
private String problem_statement;

    private String code;

 @JsonProperty("test_cases")
private List<PythonTestCaseDTO> test_cases;

    private String language = "python";

   private String difficulty_level="intermediate";

    // Getters and Setters

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

    public String getProblem_statement() {
    return problem_statement;
}

public void setProblem_statement(String problem_statement) {
    this.problem_statement = problem_statement;
}

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

  public List<PythonTestCaseDTO> getTest_cases() {
    return test_cases;
}

public void setTest_cases(List<PythonTestCaseDTO> test_cases) {
    this.test_cases = test_cases;
}

    public String getLanguage() {
        return language;
    }

    public void setLanguage(String language) {
        this.language = language;
    }

    public String getDifficulty_level() {
    return difficulty_level;
}

public void setDifficulty_level(String difficulty_level) {
    this.difficulty_level = difficulty_level;
}
}