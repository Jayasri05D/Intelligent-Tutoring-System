package com.example.backend.dto;
//this is for the summary of the test cases in the frontend
public class TestSummaryDTO {

    private int passed;
    private int total;
    private String score;
    private boolean all_passed;

    public int getPassed() {
        return passed;
    }

    public void setPassed(int passed) {
        this.passed = passed;
    }

    public int getTotal() {
        return total;
    }

    public void setTotal(int total) {
        this.total = total;
    }

    public String getScore() {
        return score;
    }

    public void setScore(String score) {
        this.score = score;
    }

    public boolean isAll_passed() {
        return all_passed;
    }

    public void setAll_passed(boolean all_passed) {
        this.all_passed = all_passed;
    }
}