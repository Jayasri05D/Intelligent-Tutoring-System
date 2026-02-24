package com.example.backend.dto;

public class ViolationDTO {
       private String rule_id;
    private String concept;
    private int line;
    private double confidence;
    public String getRule_id() {
        return rule_id;
    }
    public void setRule_id(String rule_id) {
        this.rule_id = rule_id;
    }
    public String getConcept() {
        return concept;
    }
    public void setConcept(String concept) {
        this.concept = concept;
    }
    public int getLine() {
        return line;
    }
    public void setLine(int line) {
        this.line = line;
    }
    public double getConfidence() {
        return confidence;
    }
    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }

}
