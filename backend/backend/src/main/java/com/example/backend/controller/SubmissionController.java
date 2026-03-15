
// package com.example.backend.controller;

// import com.example.backend.dto.CodeRequest;
// import com.example.backend.dto.CompilerResponseDTO;
// import com.example.backend.dto.PythonTestCaseDTO;
// import com.example.backend.dto.TestCaseResultDTO;
// import com.example.backend.entity.TestCase;
// import com.example.backend.repository.TestCaseRepository;
// import com.example.backend.dto.AnalyzeResponseDTO;
// import com.example.backend.service.CodeExecutionService;
// import com.example.backend.service.SubmissionService;

// import io.swagger.v3.oas.annotations.Operation;
// import io.swagger.v3.oas.annotations.tags.Tag;

// import java.util.ArrayList;
// import java.util.List;

// import org.springframework.http.ResponseEntity;
// import org.springframework.web.bind.annotation.*;

// @RestController
// @RequestMapping("/api/submissions")
// @CrossOrigin
// @Tag(name = "Submissions", description = "Endpoints for code submission and analysis")
// public class SubmissionController {
//         private final TestCaseRepository testCaseRepository;
//     private final CodeExecutionService codeExecutionService;
//     private final SubmissionService submissionService;
      
//     public SubmissionController(SubmissionService submissionService,
//                                 TestCaseRepository testCaseRepository,
//                                 CodeExecutionService codeExecutionService) {
//         this.submissionService = submissionService;
//         this.testCaseRepository = testCaseRepository;
//         this.codeExecutionService = codeExecutionService;
//     }

//     // =========================================================
//     // 🧠 1️⃣ Semantic Analysis ONLY (No test case execution)
//     // =========================================================
//     @PostMapping("/analyze")
//     @Operation(
//             summary = "Analyze Code Only",
//             description = "Performs semantic analysis using AI and stores submission without running test cases"
//     )
//     public AnalyzeResponseDTO analyzeOnly(@RequestBody CodeRequest request) {
//         return submissionService.analyzeAndSave(request);
//     }


//     // =========================================================
//     // 🚀 2️⃣ Full Submission (Run + Validate + Analyze + Save)
//     // =========================================================
//     @PostMapping("/{questionId}")
//     @Operation(
//             summary = "Submit Code",
//             description = "Runs code, validates test cases, performs AI analysis and stores submission"
//     )
//     public CompilerResponseDTO submitCode(
//             @PathVariable Long questionId,
//             @RequestBody CodeRequest request
//     ) {
//         return submissionService.submitCode(questionId, request);
//     }

//      @PostMapping("/run/{questionId}")
//     public ResponseEntity<?> runTestCases(@PathVariable Long questionId,
//                                           @RequestBody CodeRequest request) {

//         List<TestCase> testCases = testCaseRepository.findByQuestionId(questionId);
        
    
//         List<TestCaseResultDTO> results = new ArrayList<>();

//         for (TestCase tc : testCases) {
//             TestCaseResultDTO result = new TestCaseResultDTO();
//             result.setId(tc.getId());
//             result.setInput(tc.getInput());
//             result.setExpectedOutput(tc.getExpectedOutput());

//             String output = codeExecutionService.executeCode(request.getCode(), request.getLanguage(), tc.getInput());
//             result.setActualOutput(output);
//             result.setPassed(tc.getExpectedOutput().trim().equals(output.trim()));

//             results.add(result);
//         }

//         return ResponseEntity.ok(results);
//     }
// }
package com.example.backend.controller;

import com.example.backend.dto.AnalyzeResponseDTO;
import com.example.backend.dto.CodeRequest;
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

    // ── removed CodeExecutionService and TestCaseRepository
    // ── they were only used by runTestCases which is now deleted
    public SubmissionController(SubmissionService submissionService) {
        this.submissionService = submissionService;
    }

    // =========================================================
    // POST /api/submissions/analyze
    // Analyze without a specific questionId in the path
    // CodeRequest must contain questionId as a body field
    // =========================================================
    @PostMapping("/analyze")
    @Operation(
        summary = "Analyze Code",
        description = "Sends code to Python AI service, runs test cases, returns logical errors"
    )
    public AnalyzeResponseDTO analyzeOnly(@RequestBody CodeRequest request) {
        return submissionService.analyzeAndSave(request);
    }

    // =========================================================
    // POST /api/submissions/{questionId}
    // Full submission — questionId comes from path variable
    // =========================================================
    @PostMapping("/{questionId}")
    @Operation(
        summary = "Submit Code",
        description = "Full submission — runs tests, AI analysis, saves to DB, returns full result"
    )
    public AnalyzeResponseDTO submitCode(           // ← changed from CompilerResponseDTO
            @PathVariable Long questionId,
            @RequestBody CodeRequest request
    ) {
        return submissionService.submitCode(questionId, request);
    }

    // =========================================================
    // REMOVED: runTestCases
    // Reason: used CodeExecutionService which is deleted.
    // Python AI service runs test cases internally — no need
    // to run them again in Java.
    // =========================================================
}
