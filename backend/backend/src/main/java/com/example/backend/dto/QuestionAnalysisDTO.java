package com.example.backend.dto;

import java.util.List;
//for Analyse Response DTO this was added
public class QuestionAnalysisDTO {

    private String detected_operation;
    private List<String> expected_concepts;
    private String expected_return_type;
    private String input_structure;
    private List<String> edge_cases_in_problem;

    public String getDetected_operation() {
        return detected_operation;
    }

    public void setDetected_operation(String detected_operation) {
        this.detected_operation = detected_operation;
    }

    public List<String> getExpected_concepts() {
        return expected_concepts;
    }

    public void setExpected_concepts(List<String> expected_concepts) {
        this.expected_concepts = expected_concepts;
    }

    public String getExpected_return_type() {
        return expected_return_type;
    }

    public void setExpected_return_type(String expected_return_type) {
        this.expected_return_type = expected_return_type;
    }

    public String getInput_structure() {
        return input_structure;
    }

    public void setInput_structure(String input_structure) {
        this.input_structure = input_structure;
    }

    public List<String> getEdge_cases_in_problem() {
        return edge_cases_in_problem;
    }

    public void setEdge_cases_in_problem(List<String> edge_cases_in_problem) {
        this.edge_cases_in_problem = edge_cases_in_problem;
    }
}