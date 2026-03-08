package com.example.backend.dto;

import java.util.List;

public class LogicalErrorDTO {

    private String error_id;
    private String severity;
    private String category;
    private String what;
    private String where;
    private String why;
    private String hint;
    private Integer line;
    private String code_snippet;
    private double confidence;
    private List<Integer> related_test_cases;

    public String getError_id() {
        return error_id;
    }

    public void setError_id(String error_id) {
        this.error_id = error_id;
    }

    public String getSeverity() {
        return severity;
    }

    public void setSeverity(String severity) {
        this.severity = severity;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getWhat() {
        return what;
    }

    public void setWhat(String what) {
        this.what = what;
    }

    public String getWhere() {
        return where;
    }

    public void setWhere(String where) {
        this.where = where;
    }

    public String getWhy() {
        return why;
    }

    public void setWhy(String why) {
        this.why = why;
    }

    public String getHint() {
        return hint;
    }

    public void setHint(String hint) {
        this.hint = hint;
    }

    public Integer getLine() {
        return line;
    }

    public void setLine(Integer line) {
        this.line = line;
    }

    public String getCode_snippet() {
        return code_snippet;
    }

    public void setCode_snippet(String code_snippet) {
        this.code_snippet = code_snippet;
    }

    public double getConfidence() {
        return confidence;
    }

    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }

    public List<Integer> getRelated_test_cases() {
        return related_test_cases;
    }

    public void setRelated_test_cases(List<Integer> related_test_cases) {
        this.related_test_cases = related_test_cases;
    }
}