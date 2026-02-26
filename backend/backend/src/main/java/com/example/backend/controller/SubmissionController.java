package com.example.backend.controller;

import com.example.backend.dto.CodeRequest;
import com.example.backend.dto.AnalyzeResponseDTO;
import com.example.backend.service.SubmissionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/submissions")
@CrossOrigin
@Tag(name = "Submissions", description = "Endpoints for code submission and analysis")
public class SubmissionController {

    private final SubmissionService submissionService;

    public SubmissionController(SubmissionService submissionService) {
        this.submissionService = submissionService;
    }

    @PostMapping("/analyze")
    @Operation(
            summary = "Analyze code",
            description = "Submits student code for semantic analysis and returns detected violations"
    )
    public AnalyzeResponseDTO analyze(@RequestBody CodeRequest request) {
        return submissionService.analyzeAndSave(request);
    }
}