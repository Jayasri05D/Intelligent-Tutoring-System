package com.example.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ViolationDTO {
       @JsonProperty("rule_id")
    private String ruleId;

    private String concept;

    private int line;

    private double confidence;

    @JsonProperty("violated_principle")
    private String violatedPrinciple;

    private String explanation;

    @JsonProperty("why_it_matters")
    private String whyItMatters;

    public String getRuleId() {
        return ruleId;
    }

    public void setRuleId(String ruleId) {
        this.ruleId = ruleId;
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

    public String getViolatedPrinciple() {
        return violatedPrinciple;
    }

    public void setViolatedPrinciple(String violatedPrinciple) {
        this.violatedPrinciple = violatedPrinciple;
    }

    public String getExplanation() {
        return explanation;
    }

    public void setExplanation(String explanation) {
        this.explanation = explanation;
    }

    public String getWhyItMatters() {
        return whyItMatters;
    }

    public void setWhyItMatters(String whyItMatters) {
        this.whyItMatters = whyItMatters;
    }

   
}
