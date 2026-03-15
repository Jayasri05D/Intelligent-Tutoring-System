package com.example.backend.dto;

import java.util.List;
import java.util.Map;

public class LearnerProfileDTO {

    private int session_count;
    private List<String> strengths;
    private List<String> weaknesses;
    private List<String> moderate;
    private List<Map<String, Object>> repeated_misconceptions;

    public int getSession_count() { return session_count; }
    public void setSession_count(int session_count) { this.session_count = session_count; }

    public List<String> getStrengths() { return strengths; }
    public void setStrengths(List<String> strengths) { this.strengths = strengths; }

    public List<String> getWeaknesses() { return weaknesses; }
    public void setWeaknesses(List<String> weaknesses) { this.weaknesses = weaknesses; }

    public List<String> getModerate() { return moderate; }
    public void setModerate(List<String> moderate) { this.moderate = moderate; }

    public List<Map<String, Object>> getRepeated_misconceptions() { return repeated_misconceptions; }
    public void setRepeated_misconceptions(List<Map<String, Object>> repeated_misconceptions) {
        this.repeated_misconceptions = repeated_misconceptions;
    }
}