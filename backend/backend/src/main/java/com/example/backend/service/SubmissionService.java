
// package com.example.backend.service;

// import com.example.backend.dto.*;
// import com.example.backend.entity.*;
// import com.example.backend.repository.*;
// import com.fasterxml.jackson.databind.ObjectMapper;

// import org.springframework.stereotype.Service;
// import org.springframework.web.reactive.function.client.WebClient;

// import java.util.ArrayList;
// import java.util.List;

// @Service
// public class SubmissionService {

//     private final WebClient webClient;
//     private final StudentRepository studentRepository;
//     private final SubmissionRepository submissionRepository;
//     private final MisconceptionRepository misconceptionRepository;
//     private final QuestionRepository questionRepository;
//     private final TestCaseRepository testCaseRepository;

//     public SubmissionService(
//             WebClient webClient,
//             StudentRepository studentRepository,
//             SubmissionRepository submissionRepository,
//             MisconceptionRepository misconceptionRepository,
//             QuestionRepository questionRepository,
//             TestCaseRepository testCaseRepository
//     ) {
//         this.webClient = webClient;
//         this.studentRepository = studentRepository;
//         this.submissionRepository = submissionRepository;
//         this.misconceptionRepository = misconceptionRepository;
//         this.questionRepository = questionRepository;
//         this.testCaseRepository = testCaseRepository;
//     }

//     // =========================================================
//     // 🧠 1️⃣ ANALYZE ONLY (Semantic AI Analysis)
//     // =========================================================
//     // public AnalyzeResponseDTO analyzeAndSave(CodeRequest request) {
         
//     //     AnalyzeResponseDTO response = webClient.post()
//     //             .uri("/analyze")
//     //             .bodyValue(request)
//     //             .retrieve()
//     //             .bodyToMono(AnalyzeResponseDTO.class)
//     //             .block();

//     //     Student student = studentRepository.findById(request.getStudentId())
//     //             .orElseThrow(() -> new RuntimeException("Student not found"));

//     //     Submission submission = new Submission();
//     //     submission.setCodeText(request.getCode());
//     //     submission.setLanguage(request.getLanguage());
//     //     submission.setHasSyntaxError(response.isHas_syntax_error());
//     //     submission.setPassed(false);
//     //     submission.setStudent(student);

//     //     Submission savedSubmission = submissionRepository.save(submission);

//     //     if (response.getViolations() != null) {
//     //         for (ViolationDTO v : response.getViolations()) {
//     //             Misconception m = new Misconception();
//     //             m.setRuleId(v.getRuleId());
//     //             m.setConcept(v.getConcept());
//     //             m.setLineNumber(v.getLine());
//     //             m.setConfidence(v.getConfidence());
//     //             m.setSubmission(savedSubmission);
//     //             misconceptionRepository.save(m);
//     //         }
//     //     }

//     //     return response;
//     // }

//     public AnalyzeResponseDTO analyzeAndSave(CodeRequest request) {

//     try {

//         // =====================================================
//         // 1️⃣ Fetch Student
//         // =====================================================
//         Student student = studentRepository.findById(request.getStudentId())
//                 .orElseThrow(() -> new RuntimeException("Student not found"));

//                 // 1️⃣ Fetch Question from DB
//     Question question = questionRepository.findById(request.getQuestionId())
//             .orElseThrow(() -> new RuntimeException("Question not found"));

//     // 2️⃣ Fetch Test Cases from DB
//     List<TestCase> testCaseEntities =
//             testCaseRepository.findByQuestionId(question.getId());

//     // 3️⃣ Convert TestCase Entity → DTO
//     List<TestCaseDTO> testCaseDTOs = testCaseEntities.stream()
//             .map(tc -> {
//                 TestCaseDTO dto = new TestCaseDTO();
//                 dto.setInput(tc.getInput());
//                 dto.setExpectedOutput(tc.getExpectedOutput());
//                 return dto;
//             })
//             .toList();

//         // =====================================================
//         // 2️⃣ Build AnalyzeRequestDTO (DO NOT send CodeRequest)
//         // =====================================================
//         AnalyzeRequestDTO analyzeRequest = new AnalyzeRequestDTO();
        
//         analyzeRequest.setCode(request.getCode());
//         analyzeRequest.setLanguage(request.getLanguage());
//         analyzeRequest.setStudentId(request.getStudentId());
// analyzeRequest.setQuestionId(question.getId().toString());
// analyzeRequest.setCode(request.getCode());
// analyzeRequest.setLanguage(request.getLanguage());
// analyzeRequest.setProblemStatement(question.getDescription());
// analyzeRequest.setTestCases(testCaseDTOs);

//         // If your analyze endpoint needs problem_statement,
//         // fetch question and set it here (optional)
//         // analyzeRequest.setProblemStatement(...);

//         // =====================================================
//         // 3️⃣ Call FastAPI → /analyze
//         // =====================================================
//         ObjectMapper mapper = new ObjectMapper();
// String json = mapper.writeValueAsString(request);
// System.out.println("JSON sent to Python: " + json);
//         AnalyzeResponseDTO response = webClient.post()
//                 .uri("/analyze")
//                 .bodyValue(analyzeRequest)
//                 .retrieve()
//                 .onStatus(status -> status.isError(),
//                         clientResponse -> clientResponse.bodyToMono(String.class)
//                                 .map(body -> new RuntimeException("Analyze API Error: " + body))
//                 )
//                 .bodyToMono(AnalyzeResponseDTO.class)
//                 .block();
                
//          if (response.getViolations() == null) {
//     response.setViolations(new ArrayList<>());
// }
//         if (response == null) {
//             throw new RuntimeException("Analyze API returned null response");
//         }

//         // =====================================================
//         // 4️⃣ Save Submission
//         // =====================================================
//         Submission submission = new Submission();
//         submission.setCodeText(request.getCode());
//         submission.setLanguage(request.getLanguage());
//        // submission.setHasSyntaxError(response.isHas_syntax_error());
//         submission.setPassed(false); // analyze only → no evaluation
//         submission.setStudent(student);

//         Submission savedSubmission = submissionRepository.save(submission);

//         // =====================================================
//         // 5️⃣ Save Misconceptions
//         // =====================================================
//         if (response.getViolations() != null) {

//             for (ViolationDTO v : response.getViolations()) {

//                 Misconception misconception = new Misconception();
//                 misconception.setRuleId(v.getRuleId());
//                 misconception.setConcept(v.getConcept());
//                 misconception.setLineNumber(v.getLine());
//                 misconception.setConfidence(v.getConfidence());
//                 misconception.setSubmission(savedSubmission);

//                 misconceptionRepository.save(misconception);
//             }
//         }

//         return response;

//     } catch (Exception e) {

//         throw new RuntimeException("Analyze failed: " + e.getMessage());
//     }
// }

//     // =========================================================
//     // 🚀 2️⃣ FULL SUBMISSION (Evaluate + Analyze + Save)
//     // =========================================================
//     public CompilerResponseDTO submitCode(Long questionId, CodeRequest request) {

//         try {

//             // ============================
//             // 1️⃣ Fetch Student & Question
//             // ============================
//             Student student = studentRepository.findById(request.getStudentId())
//                     .orElseThrow(() -> new RuntimeException("Student not found"));

//             Question question = questionRepository.findById(questionId)
//                     .orElseThrow(() -> new RuntimeException("Question not found"));

//             // ============================
//             // 2️⃣ Fetch Test Cases
//             // ============================
//             List<TestCase> testCases = testCaseRepository.findByQuestionId(questionId);

//             if (testCases.isEmpty()) {
//                 return new CompilerResponseDTO(
//                         "",
//                         "No test cases found for this question.",
//                         false
//                 );
//             }

//             // ============================
//             // 3️⃣ Convert TestCases → PythonTestCaseDTO
//             // ============================
//             List<PythonTestCaseDTO> pythonTestCases = testCases.stream()
//                     .map(tc -> {
//                         PythonTestCaseDTO dto = new PythonTestCaseDTO();
//                         dto.setInput(tc.getInput());
//                         dto.setExpectedOutput(tc.getExpectedOutput());
//                         return dto;
//                     })
//                     .toList();

//             // ============================
//             // 4️⃣ Build EvaluationRequestDTO
//             // ============================
//             EvaluationRequestDTO evaluationRequest = new EvaluationRequestDTO();
//             evaluationRequest.setStudentId(request.getStudentId());
//             evaluationRequest.setQuestionId(questionId.toString());
//             evaluationRequest.setProblemStatement(question.getDescription());
//             evaluationRequest.setCode(request.getCode());
//             evaluationRequest.setLanguage(request.getLanguage());
//             evaluationRequest.setTestCases(pythonTestCases);

//             // ============================
//             // 5️⃣ Call FastAPI → /evaluate
//             // ============================
//             EvaluationRequestDTO evaluationResponse = webClient.post()
//                     .uri("/evaluate")
//                     .bodyValue(evaluationRequest)
//                     .retrieve()
//                     .bodyToMono(EvaluationRequestDTO.class)
//                     .block();

//             // ============================
//             // 6️⃣ Call FastAPI → /analyze
//             // ============================
//           AnalyzeRequestDTO analyzeRequest = new AnalyzeRequestDTO();
// analyzeRequest.setCode(request.getCode());
// analyzeRequest.setLanguage(request.getLanguage());
// analyzeRequest.setProblemStatement(question.getDescription());

// AnalyzeResponseDTO analyzeResponse = webClient.post()
//         .uri("/analyze")
//         .bodyValue(analyzeRequest)
//         .retrieve()
//         .bodyToMono(AnalyzeResponseDTO.class)
//         .block();

//             // ============================
//             // 7️⃣ Save Submission
//             // ============================
//             Submission submission = new Submission();
//             submission.setCodeText(request.getCode());
//             submission.setLanguage(request.getLanguage());
//             //submission.setHasSyntaxError(analyzeResponse.isHas_syntax_error());
//             submission.setPassed(evaluationResponse.isPassed());
//             submission.setRuntimeOutput(evaluationResponse.getRuntimeOutput());
//             submission.setRuntimeError(evaluationResponse.getRuntimeError());
//             submission.setStudent(student);
//             submission.setQuestion(question);

//             Submission savedSubmission = submissionRepository.save(submission);

//             // ============================
//             // 8️⃣ Save Misconceptions
//             // ============================
//             if (analyzeResponse.getViolations() != null) {
//                 for (ViolationDTO v : analyzeResponse.getViolations()) {
//                     Misconception m = new Misconception();
//                     m.setRuleId(v.getRuleId());
//                     m.setConcept(v.getConcept());
//                     m.setLineNumber(v.getLine());
//                     m.setConfidence(v.getConfidence());
//                     m.setSubmission(savedSubmission);
//                     misconceptionRepository.save(m);
//                 }
//             }

//             // ============================
//             // 9️⃣ Return Response to Frontend
//             // ============================
//             return new CompilerResponseDTO(
//                     evaluationResponse.getRuntimeOutput(),
//                     evaluationResponse.getRuntimeError(),
//                     evaluationResponse.isPassed()
//             );

//         } catch (Exception e) {

//             return new CompilerResponseDTO(
//                     "",
//                     e.getMessage(),
//                     false
//             );
//         }
//     }
// }

// package com.example.backend.service;

// import com.example.backend.dto.*;
// import com.example.backend.entity.*;
// import com.example.backend.repository.*;
// import org.springframework.stereotype.Service;
// import org.springframework.web.reactive.function.client.WebClient;

// import java.util.List;

// @Service
// public class SubmissionService {

//     private final WebClient webClient;
//     private final StudentRepository studentRepository;
//     private final SubmissionRepository submissionRepository;
//     private final MisconceptionRepository misconceptionRepository;
//     private final QuestionRepository questionRepository;
//     private final TestCaseRepository testCaseRepository;

//     public SubmissionService(
//             WebClient webClient,
//             StudentRepository studentRepository,
//             SubmissionRepository submissionRepository,
//             MisconceptionRepository misconceptionRepository,
//             QuestionRepository questionRepository,
//             TestCaseRepository testCaseRepository
//     ) {
//         this.webClient = webClient;
//         this.studentRepository = studentRepository;
//         this.submissionRepository = submissionRepository;
//         this.misconceptionRepository = misconceptionRepository;
//         this.questionRepository = questionRepository;
//         this.testCaseRepository = testCaseRepository;
//     }

//     // =========================================================
//     // analyzeAndSave — called by POST /api/submissions/analyze
//     // Sends code to Python /analyze, saves results to MySQL
//     // =========================================================
//     public AnalyzeResponseDTO analyzeAndSave(CodeRequest request) {
//         try {

//             // 1. Fetch student
//             Student student = studentRepository.findById(request.getStudentId())
//                     .orElseThrow(() -> new RuntimeException("Student not found"));

//             // 2. Fetch question
//             Question question = questionRepository.findById(request.getQuestionId())
//                     .orElseThrow(() -> new RuntimeException("Question not found"));

//             // 3. Fetch test cases
//             List<TestCase> testCaseEntities =
//                     testCaseRepository.findByQuestionId(question.getId());

//             if (testCaseEntities.isEmpty()) {
//                 throw new RuntimeException("No test cases found for question: " + question.getId());
//             }

//             // 4. Convert TestCase entities → PythonTestCaseDTO
//             //    IMPORTANT: use PythonTestCaseDTO, not TestCaseDTO
//             //    PythonTestCaseDTO uses @JsonProperty("expected_output")
//             //    which matches exactly what Python expects
//             List<PythonTestCaseDTO> pythonTestCases = testCaseEntities.stream()
//                     .map(tc -> {
//                         PythonTestCaseDTO dto = new PythonTestCaseDTO();
//                         dto.setInput(tc.getInput());
//                         dto.setExpectedOutput(tc.getExpectedOutput());
//                         return dto;
//                     })
//                     .toList();

//             // 5. Build PythonAnalyzeRequestDTO
//             //    This matches EXACTLY what Python v5 /analyze expects
//             PythonAnalyzeRequestDTO pythonRequest = new PythonAnalyzeRequestDTO();
//             pythonRequest.setStudentId(String.valueOf(request.getStudentId()));
//             pythonRequest.setQuestionId(question.getId().toString());
//             pythonRequest.setProblem_statement(question.getDescription());
//             pythonRequest.setCode(request.getCode());
//             pythonRequest.setLanguage(
//                 request.getLanguage() != null ? request.getLanguage() : "python"
//             );
//             pythonRequest.setTest_cases(pythonTestCases);
//             pythonRequest.setDifficulty_level(
//                 question.getDifficultyLevel() != null ? question.getDifficultyLevel() : "intermediate"
//             );

//             // 6. Call Python /analyze — ONE call, does everything
//             AnalyzeResponseDTO response = webClient.post()
//                     .uri("/analyze")
//                     .bodyValue(pythonRequest)
//                     .retrieve()
//                     .onStatus(
//                         status -> status.isError(),
//                         clientResponse -> clientResponse.bodyToMono(String.class)
//                             .map(body -> new RuntimeException("Python API error: " + body))
//                     )
//                     .bodyToMono(AnalyzeResponseDTO.class)
//                     .block();

//             if (response == null) {
//                 throw new RuntimeException("Python /analyze returned null");
//             }

//             // 7. Save submission to MySQL
//             Submission submission = new Submission();
//             submission.setCodeText(request.getCode());
//             submission.setLanguage(request.getLanguage());
//             submission.setStudent(student);
//             submission.setQuestion(question);
//             // passed = true only if ALL test cases passed
//             submission.setPassed(
//                 response.getTest_summary() != null && response.getTest_summary().isAll_passed()
//             );

//             Submission savedSubmission = submissionRepository.save(submission);

//             // 8. Save logical errors as misconceptions
//             //    logical_errors replaces the old violations list
//             if (response.getLogical_errors() != null) {
//                 for (LogicalErrorDTO err : response.getLogical_errors()) {
//                     Misconception m = new Misconception();
//                     m.setRuleId(err.getError_id());        // error_id → ruleId
//                     m.setConcept(err.getCategory());       // category → concept
//                     m.setLineNumber(
//                         err.getLine() != null ? err.getLine() : 0
//                     );
//                     m.setConfidence(err.getConfidence());
//                     m.setSubmission(savedSubmission);
//                     misconceptionRepository.save(m);
//                 }
//             }

//             return response;

//         } catch (Exception e) {
//             throw new RuntimeException("analyzeAndSave failed: " + e.getMessage());
//         }
//     }

//     // =========================================================
//     // submitCode — called by POST /api/submissions/{questionId}
//     // Same as analyzeAndSave but triggered from a different route
//     // Python /analyze already runs tests + analyzes in one call
//     // so this is now identical — just a named alias
//     // =========================================================
//     public AnalyzeResponseDTO submitCode(Long questionId, CodeRequest request) {
//         // Set questionId from path variable into the request
//         request.setQuestionId(questionId);
//         return analyzeAndSave(request);
//     }

//     // runCode — called by POST /api/submissions/run
//     // This is the "dry run" compiler — just executes, no AI analysis
//     // Python handles execution internally, so we just return a placeholder
//     // OR you can remove this entirely if your frontend doesn't use it
//     public CompilerResponseDTO runCode(CodeRequest request) {
//         // Python runs the actual code inside /analyze
//         // This endpoint is only useful if you want a "run without analyze" feature
//         // For now return a message telling the frontend to use /analyze
//         return new CompilerResponseDTO(
//             "",
//             "Use /api/submissions/{questionId} to run and analyze together.",
//             false
//         );
//     }
// }

package com.example.backend.service;

import com.example.backend.dto.*;
import com.example.backend.entity.*;
import com.example.backend.repository.*;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.ArrayList;
import java.util.List;

@Service
public class SubmissionService {

    private final WebClient webClient;
    private final StudentRepository studentRepository;
    private final SubmissionRepository submissionRepository;
    private final MisconceptionRepository misconceptionRepository;
    private final QuestionRepository questionRepository;
    private final TestCaseRepository testCaseRepository;

    public SubmissionService(
            WebClient webClient,
            StudentRepository studentRepository,
            SubmissionRepository submissionRepository,
            MisconceptionRepository misconceptionRepository,
            QuestionRepository questionRepository,
            TestCaseRepository testCaseRepository
    ) {
        this.webClient = webClient;
        this.studentRepository = studentRepository;
        this.submissionRepository = submissionRepository;
        this.misconceptionRepository = misconceptionRepository;
        this.questionRepository = questionRepository;
        this.testCaseRepository = testCaseRepository;
    }

    // =========================================================
    // Analyze code and save results
    // =========================================================
    public AnalyzeResponseDTO analyzeAndSave(CodeRequest request) {

        try {

            // 1. Fetch student
            Student student = studentRepository.findById(request.getStudentId())
                    .orElseThrow(() -> new RuntimeException("Student not found"));

            // 2. Fetch question
            Question question = questionRepository.findById(request.getQuestionId())
                    .orElseThrow(() -> new RuntimeException("Question not found"));

            // 3. Fetch test cases
            List<TestCase> testCaseEntities =
                    testCaseRepository.findByQuestionId(question.getId());

            if (testCaseEntities == null || testCaseEntities.isEmpty()) {
                throw new RuntimeException("No test cases found for question: " + question.getId());
            }

            // 4. Convert DB TestCase → PythonTestCaseDTO
            List<PythonTestCaseDTO> pythonTestCases = new ArrayList<>();

            for (TestCase tc : testCaseEntities) {
                PythonTestCaseDTO dto = new PythonTestCaseDTO();
                dto.setInput(tc.getInput());
                dto.setExpectedOutput(tc.getExpectedOutput());
                pythonTestCases.add(dto);
            }

            // 5. Build request for Python AI service
            PythonAnalyzeRequestDTO pythonRequest = new PythonAnalyzeRequestDTO();

            pythonRequest.setStudentId((request.getStudentId()));
            pythonRequest.setQuestionId(String.valueOf(question.getId()));
            pythonRequest.setProblem_statement(question.getDescription());
            pythonRequest.setCode(request.getCode());

            pythonRequest.setLanguage(
                    request.getLanguage() != null ? request.getLanguage() : "python"
            );

            pythonRequest.setTest_cases(pythonTestCases);

            pythonRequest.setDifficulty_level(
                    question.getDifficultyLevel() != null
                            ? question.getDifficultyLevel()
                            : "intermediate"
            );

            // 6. Call Python AI service
            AnalyzeResponseDTO response = webClient.post()
                    .uri("/analyze")
                    .bodyValue(pythonRequest)
                    .retrieve()
                    .bodyToMono(AnalyzeResponseDTO.class)
                    .block();

            if (response == null) {
                throw new RuntimeException("Python service returned null response");
            }

            // 7. Save submission
            Submission submission = new Submission();
            submission.setCodeText(request.getCode());
            submission.setLanguage(pythonRequest.getLanguage());
            submission.setStudent(student);
            submission.setQuestion(question);

            boolean passed = false;
            if (response.getTest_summary() != null) {
                passed = response.getTest_summary().isAll_passed();
            }

            submission.setPassed(passed);

            Submission savedSubmission = submissionRepository.save(submission);

            // 8. Save logical errors → misconceptions
            if (response.getLogical_errors() != null) {

                for (LogicalErrorDTO err : response.getLogical_errors()) {

                    Misconception m = new Misconception();

                    m.setRuleId(err.getError_id());
                    m.setConcept(err.getCategory());

                    m.setLineNumber(
                            err.getLine() != null ? err.getLine() : 0
                    );

                    m.setConfidence(err.getConfidence());

                    m.setSubmission(savedSubmission);

                    misconceptionRepository.save(m);
                }
            }

            return response;

        } catch (Exception e) {
            throw new RuntimeException("analyzeAndSave failed: " + e.getMessage(), e);
        }
    }

    // =========================================================
    // Submit code (alias of analyzeAndSave)
    // =========================================================
    public AnalyzeResponseDTO submitCode(Long questionId, CodeRequest request) {

        request.setQuestionId(questionId);
        return analyzeAndSave(request);
    }

    // =========================================================
    // Run code without analysis (optional)
    // =========================================================
    public CompilerResponseDTO runCode(CodeRequest request) {

        return new CompilerResponseDTO(
                "",
                "Use /api/submissions/{questionId} to run and analyze together.",
                false
        );
    }
}