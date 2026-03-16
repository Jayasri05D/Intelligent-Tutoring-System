package com.example.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class PythonTestCaseDTO {

    private String input;

    @JsonProperty("expected_output")
    private String expectedOutput;

    public String getInput() {
        return input;
    }

    public void setInput(String input) {
        this.input = input;
    }

    public String getExpectedOutput() {
        return expectedOutput;
    }

    public void setExpectedOutput(String expectedOutput) {
        this.expectedOutput = expectedOutput;
    }
}