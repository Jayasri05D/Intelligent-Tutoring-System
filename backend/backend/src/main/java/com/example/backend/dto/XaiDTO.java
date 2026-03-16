package com.example.backend.dto;

import java.util.List;

public class XaiDTO {

    private List<String> concept_path;
    private double confidence;
    private int retrieved_doc_count;

    public List<String> getConcept_path() { return concept_path; }
    public void setConcept_path(List<String> concept_path) { this.concept_path = concept_path; }

    public double getConfidence() { return confidence; }
    public void setConfidence(double confidence) { this.confidence = confidence; }

    public int getRetrieved_doc_count() { return retrieved_doc_count; }
    public void setRetrieved_doc_count(int retrieved_doc_count) { this.retrieved_doc_count = retrieved_doc_count; }
}