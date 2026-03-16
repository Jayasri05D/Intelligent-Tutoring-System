// package com.example.backend.dto;

// import java.util.List;
// //for Analyse Response DTO this was added
// public class QuestionAnalysisDTO {

//     private String detected_operation;
//     private List<String> expected_concepts;
//     private String expected_return_type;
//     private String input_structure;
//     private List<String> edge_cases_in_problem;

//     public String getDetected_operation() {
//         return detected_operation;
//     }

//     public void setDetected_operation(String detected_operation) {
//         this.detected_operation = detected_operation;
//     }

//     public List<String> getExpected_concepts() {
//         return expected_concepts;
//     }

//     public void setExpected_concepts(List<String> expected_concepts) {
//         this.expected_concepts = expected_concepts;
//     }

//     public String getExpected_return_type() {
//         return expected_return_type;
//     }

//     public void setExpected_return_type(String expected_return_type) {
//         this.expected_return_type = expected_return_type;
//     }

//     public String getInput_structure() {
//         return input_structure;
//     }

//     public void setInput_structure(String input_structure) {
//         this.input_structure = input_structure;
//     }

//     public List<String> getEdge_cases_in_problem() {
//         return edge_cases_in_problem;
//     }

//     public void setEdge_cases_in_problem(List<String> edge_cases_in_problem) {
//         this.edge_cases_in_problem = edge_cases_in_problem;
//     }
// }

//needed for ai implimentation
package com.example.backend.dto;

import java.util.List;

public class QuestionAnalysisDTO {

    private String operation_summary;
    private List<String> required_concepts;
    private List<String> required_structures;
    private String expected_return_type;
    private String input_description;
    private List<String> edge_cases;
    private String correct_approach;

    public String getOperation_summary() { return operation_summary; }
    public void setOperation_summary(String v) { this.operation_summary = v; }

    public List<String> getRequired_concepts() { return required_concepts; }
    public void setRequired_concepts(List<String> v) { this.required_concepts = v; }

    public List<String> getRequired_structures() { return required_structures; }
    public void setRequired_structures(List<String> v) { this.required_structures = v; }

    public String getExpected_return_type() { return expected_return_type; }
    public void setExpected_return_type(String v) { this.expected_return_type = v; }

    public String getInput_description() { return input_description; }
    public void setInput_description(String v) { this.input_description = v; }

    public List<String> getEdge_cases() { return edge_cases; }
    public void setEdge_cases(List<String> v) { this.edge_cases = v; }

    public String getCorrect_approach() { return correct_approach; }
    public void setCorrect_approach(String v) { this.correct_approach = v; }
}