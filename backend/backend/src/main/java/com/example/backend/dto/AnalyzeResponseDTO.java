package com.example.backend.dto;
import java.util.List;
public class AnalyzeResponseDTO {
      private Long studentId;
    private boolean has_syntax_error;
    private List<ViolationDTO> violations;
    public Long getStudentId() {
        return studentId;
    }
    public void setStudentId(Long studentId) {
        this.studentId = studentId;
    }
    public boolean isHas_syntax_error() {
        return has_syntax_error;
    }
    public void setHas_syntax_error(boolean has_syntax_error) {
        this.has_syntax_error = has_syntax_error;
    }
    public List<ViolationDTO> getViolations() {
        return violations;
    }
    public void setViolations(List<ViolationDTO> violations) {
        this.violations = violations;
    }

    
}
