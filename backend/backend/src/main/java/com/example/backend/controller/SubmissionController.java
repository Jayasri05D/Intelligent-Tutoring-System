// package com.example.backend.controller;

// import com.example.backend.dto.CodeRequest;
// import com.example.backend.dto.CompilerResponseDTO;
// import com.example.backend.entity.Question;
// import com.example.backend.repository.QuestionRepository;
// import com.example.backend.dto.AnalyzeResponseDTO;
// import com.example.backend.service.SubmissionService;
// import io.swagger.v3.oas.annotations.Operation;
// import io.swagger.v3.oas.annotations.tags.Tag;

// import java.util.List;

// import org.springframework.web.bind.annotation.*;

// @RestController
// @RequestMapping("/api/submissions")
// @CrossOrigin
// @Tag(name = "Submissions", description = "Endpoints for code submission and analysis")
// public class SubmissionController {

//     private final SubmissionService submissionService;

//     public SubmissionController(SubmissionService submissionService) {
//         this.submissionService = submissionService;
//     }

//     @PostMapping("/analyze")
//     @Operation(
//             summary = "Analyze code",
//             description = "Submits student code for semantic analysis and returns detected violations"
//     )
//     public AnalyzeResponseDTO analyze(@RequestBody CodeRequest request) {
//         return submissionService.analyzeAndSave(request);
//     }

//     @PostMapping("/run")
// @Operation(
//         summary = "Run code",
//         description = "Executes student code and returns runtime output"
// )
// public CompilerResponseDTO run(@RequestBody CodeRequest request) {
//     return submissionService.runCode(request);
// }


// }

package com.example.backend.controller;

import com.example.backend.dto.CodeRequest;
import com.example.backend.dto.CompilerResponseDTO;
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

    // =========================================================
    // 🧠 1️⃣ Semantic Analysis ONLY (No test case execution)
    // =========================================================
    @PostMapping("/analyze")
    @Operation(
            summary = "Analyze Code Only",
            description = "Performs semantic analysis using AI and stores submission without running test cases"
    )
    public AnalyzeResponseDTO analyzeOnly(@RequestBody CodeRequest request) {
        return submissionService.analyzeAndSave(request);
    }


    // =========================================================
    // 🚀 2️⃣ Full Submission (Run + Validate + Analyze + Save)
    // =========================================================
    @PostMapping("/{questionId}")
    @Operation(
            summary = "Submit Code",
            description = "Runs code, validates test cases, performs AI analysis and stores submission"
    )
    public CompilerResponseDTO submitCode(
            @PathVariable Long questionId,
            @RequestBody CodeRequest request
    ) {
        return submissionService.submitCode(questionId, request);
    }
}