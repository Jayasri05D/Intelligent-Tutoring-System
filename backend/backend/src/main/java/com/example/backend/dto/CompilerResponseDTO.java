package com.example.backend.dto;

public class CompilerResponseDTO {

    private String runtime_output;
    private String runtime_error;

    public CompilerResponseDTO() {}

    public CompilerResponseDTO(String runtime_output, String runtime_error) {
        this.runtime_output = runtime_output;
        this.runtime_error = runtime_error;
    }

    public String getRuntime_output() {
        return runtime_output;
    }

    public void setRuntime_output(String runtime_output) {
        this.runtime_output = runtime_output;
    }

    public String getRuntime_error() {
        return runtime_error;
    }

    public void setRuntime_error(String runtime_error) {
        this.runtime_error = runtime_error;
    }
}