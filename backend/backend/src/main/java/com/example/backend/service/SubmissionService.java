
// package com.example.backend.service;

// import com.example.backend.dto.*;
// import com.example.backend.entity.*;
// import com.example.backend.repository.*;
// import org.springframework.stereotype.Service;
// import org.springframework.web.reactive.function.client.WebClient;

// import java.io.*;
// import java.nio.file.Files;
// import java.util.List;
// import java.util.concurrent.TimeUnit;

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
//     // 🧠 1️⃣ ANALYZE ONLY (AI Semantic Analysis)
//     // =========================================================
//     public AnalyzeResponseDTO analyzeAndSave(CodeRequest request) {

//         // 1️⃣ Call FastAPI
//         AnalyzeResponseDTO response = webClient.post()
//                 .uri("/analyze")
//                 .bodyValue(request)
//                 .retrieve()
//                 .bodyToMono(AnalyzeResponseDTO.class)
//                 .block();

//         // 2️⃣ Fetch student
//         Student student = studentRepository.findById(request.getStudentId())
//                 .orElseThrow(() -> new RuntimeException("Student not found"));

//         // 3️⃣ Save submission (no question, no pass/fail)
//         Submission submission = new Submission();
//         submission.setCodeText(request.getCode());
//         submission.setLanguage(request.getLanguage());
//         submission.setHasSyntaxError(response.isHas_syntax_error());
//         submission.setPassed(false); // analyze mode
//         submission.setStudent(student);

//         Submission savedSubmission = submissionRepository.save(submission);

//         // 4️⃣ Save misconceptions
//         if (response.getViolations() != null) {
//             for (ViolationDTO v : response.getViolations()) {

//                 Misconception m = new Misconception();
//                 m.setRuleId(v.getRuleId());
//                 m.setConcept(v.getConcept());
//                 m.setLineNumber(v.getLine());
//                 m.setConfidence(v.getConfidence());
//                 m.setSubmission(savedSubmission);

//                 misconceptionRepository.save(m);
//             }
//         }

//         return response;
//     }

// public CompilerResponseDTO submitCode(Long questionId, CodeRequest request) {

//     String runtimeError = "";
//     boolean allPassed = true;
//     StringBuilder finalOutput = new StringBuilder();

//     File tempFile = null;

//     try {
//         // ============================
//         // 1️⃣ Fetch Student & Question
//         // ============================
//         Student student = studentRepository.findById(request.getStudentId())
//                 .orElseThrow(() -> new RuntimeException("Student not found"));

//         Question question = questionRepository.findById(questionId)
//                 .orElseThrow(() -> new RuntimeException("Question not found"));

//        // List<TestCase> testCases = testCaseRepository.findByQuestionId(questionId);
//         if (testCases.isEmpty()) {
//             return new CompilerResponseDTO(
//                     "",
//                     "No test cases found for this question.",
//                     false
//             );
//         }

//         // ============================
//         // 2️⃣ Create Temporary Python File
//         // ============================
//         tempFile = File.createTempFile("student_code_", ".py");
//         Files.write(tempFile.toPath(), request.getCode().getBytes());

//         // ============================
//         // 3️⃣ Execute For Each Test Case
//         // ============================
//         for (TestCase testCase : testCases) {

//             ProcessBuilder pb = new ProcessBuilder("python", tempFile.getAbsolutePath());
//             Process process = pb.start();

//             // Send input
//             try (BufferedWriter writer = new BufferedWriter(
//                     new OutputStreamWriter(process.getOutputStream()))) {
//                 writer.write(testCase.getInput());
//                 writer.newLine();
//                 writer.flush();
//             }

//             // Wait max 5 seconds
//             boolean finished = process.waitFor(5, TimeUnit.SECONDS);
//             if (!finished) {
//                 process.destroyForcibly();
//                 runtimeError = "Execution timed out";
//                 allPassed = false;
//                 break;
//             }

//             // Read Output
//             String currentOutput;
//             try (BufferedReader outputReader = new BufferedReader(
//                     new InputStreamReader(process.getInputStream()))) {

//                 StringBuilder outputBuilder = new StringBuilder();
//                 String line;
//                 while ((line = outputReader.readLine()) != null) {
//                     outputBuilder.append(line);
//                 }

//                 currentOutput = outputBuilder.toString().trim();
//             }

//             // Read Error
//             try (BufferedReader errorReader = new BufferedReader(
//                     new InputStreamReader(process.getErrorStream()))) {

//                 StringBuilder errorBuilder = new StringBuilder();
//                 String line;
//                 while ((line = errorReader.readLine()) != null) {
//                     errorBuilder.append(line);
//                 }

//                 runtimeError = errorBuilder.toString().trim();
//             }

//             // If runtime error exists → stop checking further
//             if (!runtimeError.isEmpty()) {
//                 allPassed = false;
//                 break;
//             }

//             // Compare with expected output
//             if (!currentOutput.equals(testCase.getExpectedOutput().trim())) {
//                 allPassed = false;
//             }

//             // Append to final output
//             finalOutput.append(currentOutput).append("\n");
//         }

//         // ============================
//         // 4️⃣ AI Analysis Call
//         // ============================
//         AnalyzeResponseDTO analyzeResponse = webClient.post()
//                 .uri("/analyze")
//                 .bodyValue(request)
//                 .retrieve()
//                 .bodyToMono(AnalyzeResponseDTO.class)
//                 .block();

//         // ============================
//         // 5️⃣ Save Submission
//         // ============================
//         Submission submission = new Submission();
//         submission.setCodeText(request.getCode());
//         submission.setLanguage(request.getLanguage());
//         submission.setHasSyntaxError(analyzeResponse.isHas_syntax_error());
//         submission.setPassed(allPassed);
//         submission.setRuntimeOutput(finalOutput.toString().trim());
//         submission.setRuntimeError(runtimeError);
//         submission.setStudent(student);
//         submission.setQuestion(question);

//         Submission savedSubmission = submissionRepository.save(submission);

//         // Save misconceptions
//         if (analyzeResponse.getViolations() != null) {
//             for (ViolationDTO v : analyzeResponse.getViolations()) {

//                 Misconception m = new Misconception();
//                 m.setRuleId(v.getRuleId());
//                 m.setConcept(v.getConcept());
//                 m.setLineNumber(v.getLine());
//                 m.setConfidence(v.getConfidence());
//                 m.setSubmission(savedSubmission);

//                 misconceptionRepository.save(m);
//             }
//         }

//     } catch (Exception e) {
//         runtimeError = e.getMessage();
//         allPassed = false;
//     } finally {
//         if (tempFile != null && tempFile.exists()) {
//             tempFile.delete();
//         }
//     }

//     return new CompilerResponseDTO(
//             finalOutput.toString().trim(),
//             runtimeError,
//             allPassed
//     );
// }
// }

package com.example.backend.service;

import com.example.backend.dto.*;
import com.example.backend.entity.*;
import com.example.backend.repository.*;
import com.fasterxml.jackson.databind.ObjectMapper;

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
    // 🧠 1️⃣ ANALYZE ONLY (Semantic AI Analysis)
    // =========================================================
    // public AnalyzeResponseDTO analyzeAndSave(CodeRequest request) {
         
    //     AnalyzeResponseDTO response = webClient.post()
    //             .uri("/analyze")
    //             .bodyValue(request)
    //             .retrieve()
    //             .bodyToMono(AnalyzeResponseDTO.class)
    //             .block();

    //     Student student = studentRepository.findById(request.getStudentId())
    //             .orElseThrow(() -> new RuntimeException("Student not found"));

    //     Submission submission = new Submission();
    //     submission.setCodeText(request.getCode());
    //     submission.setLanguage(request.getLanguage());
    //     submission.setHasSyntaxError(response.isHas_syntax_error());
    //     submission.setPassed(false);
    //     submission.setStudent(student);

    //     Submission savedSubmission = submissionRepository.save(submission);

    //     if (response.getViolations() != null) {
    //         for (ViolationDTO v : response.getViolations()) {
    //             Misconception m = new Misconception();
    //             m.setRuleId(v.getRuleId());
    //             m.setConcept(v.getConcept());
    //             m.setLineNumber(v.getLine());
    //             m.setConfidence(v.getConfidence());
    //             m.setSubmission(savedSubmission);
    //             misconceptionRepository.save(m);
    //         }
    //     }

    //     return response;
    // }

    public AnalyzeResponseDTO analyzeAndSave(CodeRequest request) {

    try {

        // =====================================================
        // 1️⃣ Fetch Student
        // =====================================================
        Student student = studentRepository.findById(request.getStudentId())
                .orElseThrow(() -> new RuntimeException("Student not found"));

                // 1️⃣ Fetch Question from DB
    Question question = questionRepository.findById(request.getQuestionId())
            .orElseThrow(() -> new RuntimeException("Question not found"));

    // 2️⃣ Fetch Test Cases from DB
    List<TestCase> testCaseEntities =
            testCaseRepository.findByQuestionId(question.getId());

    // 3️⃣ Convert TestCase Entity → DTO
    List<TestCaseDTO> testCaseDTOs = testCaseEntities.stream()
            .map(tc -> {
                TestCaseDTO dto = new TestCaseDTO();
                dto.setInput(tc.getInput());
                dto.setExpectedOutput(tc.getExpectedOutput());
                return dto;
            })
            .toList();

        // =====================================================
        // 2️⃣ Build AnalyzeRequestDTO (DO NOT send CodeRequest)
        // =====================================================
        AnalyzeRequestDTO analyzeRequest = new AnalyzeRequestDTO();
        
        analyzeRequest.setCode(request.getCode());
        analyzeRequest.setLanguage(request.getLanguage());
        analyzeRequest.setStudentId(request.getStudentId());
analyzeRequest.setQuestionId(question.getId().toString());
analyzeRequest.setCode(request.getCode());
analyzeRequest.setLanguage(request.getLanguage());
analyzeRequest.setProblemStatement(question.getDescription());
analyzeRequest.setTestCases(testCaseDTOs);

        // If your analyze endpoint needs problem_statement,
        // fetch question and set it here (optional)
        // analyzeRequest.setProblemStatement(...);

        // =====================================================
        // 3️⃣ Call FastAPI → /analyze
        // =====================================================
        ObjectMapper mapper = new ObjectMapper();
String json = mapper.writeValueAsString(request);
System.out.println("JSON sent to Python: " + json);
        AnalyzeResponseDTO response = webClient.post()
                .uri("/analyze")
                .bodyValue(analyzeRequest)
                .retrieve()
                .onStatus(status -> status.isError(),
                        clientResponse -> clientResponse.bodyToMono(String.class)
                                .map(body -> new RuntimeException("Analyze API Error: " + body))
                )
                .bodyToMono(AnalyzeResponseDTO.class)
                .block();
                
         if (response.getViolations() == null) {
    response.setViolations(new ArrayList<>());
}
        if (response == null) {
            throw new RuntimeException("Analyze API returned null response");
        }

        // =====================================================
        // 4️⃣ Save Submission
        // =====================================================
        Submission submission = new Submission();
        submission.setCodeText(request.getCode());
        submission.setLanguage(request.getLanguage());
       // submission.setHasSyntaxError(response.isHas_syntax_error());
        submission.setPassed(false); // analyze only → no evaluation
        submission.setStudent(student);

        Submission savedSubmission = submissionRepository.save(submission);

        // =====================================================
        // 5️⃣ Save Misconceptions
        // =====================================================
        if (response.getViolations() != null) {

            for (ViolationDTO v : response.getViolations()) {

                Misconception misconception = new Misconception();
                misconception.setRuleId(v.getRuleId());
                misconception.setConcept(v.getConcept());
                misconception.setLineNumber(v.getLine());
                misconception.setConfidence(v.getConfidence());
                misconception.setSubmission(savedSubmission);

                misconceptionRepository.save(misconception);
            }
        }

        return response;

    } catch (Exception e) {

        throw new RuntimeException("Analyze failed: " + e.getMessage());
    }
}

    // =========================================================
    // 🚀 2️⃣ FULL SUBMISSION (Evaluate + Analyze + Save)
    // =========================================================
    public CompilerResponseDTO submitCode(Long questionId, CodeRequest request) {

        try {

            // ============================
            // 1️⃣ Fetch Student & Question
            // ============================
            Student student = studentRepository.findById(request.getStudentId())
                    .orElseThrow(() -> new RuntimeException("Student not found"));

            Question question = questionRepository.findById(questionId)
                    .orElseThrow(() -> new RuntimeException("Question not found"));

            // ============================
            // 2️⃣ Fetch Test Cases
            // ============================
            List<TestCase> testCases = testCaseRepository.findByQuestionId(questionId);

            if (testCases.isEmpty()) {
                return new CompilerResponseDTO(
                        "",
                        "No test cases found for this question.",
                        false
                );
            }

            // ============================
            // 3️⃣ Convert TestCases → PythonTestCaseDTO
            // ============================
            List<PythonTestCaseDTO> pythonTestCases = testCases.stream()
                    .map(tc -> {
                        PythonTestCaseDTO dto = new PythonTestCaseDTO();
                        dto.setInput(tc.getInput());
                        dto.setExpectedOutput(tc.getExpectedOutput());
                        return dto;
                    })
                    .toList();

            // ============================
            // 4️⃣ Build EvaluationRequestDTO
            // ============================
            EvaluationRequestDTO evaluationRequest = new EvaluationRequestDTO();
            evaluationRequest.setStudentId(request.getStudentId());
            evaluationRequest.setQuestionId(questionId.toString());
            evaluationRequest.setProblemStatement(question.getDescription());
            evaluationRequest.setCode(request.getCode());
            evaluationRequest.setLanguage(request.getLanguage());
            evaluationRequest.setTestCases(pythonTestCases);

            // ============================
            // 5️⃣ Call FastAPI → /evaluate
            // ============================
            EvaluationRequestDTO evaluationResponse = webClient.post()
                    .uri("/evaluate")
                    .bodyValue(evaluationRequest)
                    .retrieve()
                    .bodyToMono(EvaluationRequestDTO.class)
                    .block();

            // ============================
            // 6️⃣ Call FastAPI → /analyze
            // ============================
          AnalyzeRequestDTO analyzeRequest = new AnalyzeRequestDTO();
analyzeRequest.setCode(request.getCode());
analyzeRequest.setLanguage(request.getLanguage());
analyzeRequest.setProblemStatement(question.getDescription());

AnalyzeResponseDTO analyzeResponse = webClient.post()
        .uri("/analyze")
        .bodyValue(analyzeRequest)
        .retrieve()
        .bodyToMono(AnalyzeResponseDTO.class)
        .block();

            // ============================
            // 7️⃣ Save Submission
            // ============================
            Submission submission = new Submission();
            submission.setCodeText(request.getCode());
            submission.setLanguage(request.getLanguage());
            //submission.setHasSyntaxError(analyzeResponse.isHas_syntax_error());
            submission.setPassed(evaluationResponse.isPassed());
            submission.setRuntimeOutput(evaluationResponse.getRuntimeOutput());
            submission.setRuntimeError(evaluationResponse.getRuntimeError());
            submission.setStudent(student);
            submission.setQuestion(question);

            Submission savedSubmission = submissionRepository.save(submission);

            // ============================
            // 8️⃣ Save Misconceptions
            // ============================
            if (analyzeResponse.getViolations() != null) {
                for (ViolationDTO v : analyzeResponse.getViolations()) {
                    Misconception m = new Misconception();
                    m.setRuleId(v.getRuleId());
                    m.setConcept(v.getConcept());
                    m.setLineNumber(v.getLine());
                    m.setConfidence(v.getConfidence());
                    m.setSubmission(savedSubmission);
                    misconceptionRepository.save(m);
                }
            }

            // ============================
            // 9️⃣ Return Response to Frontend
            // ============================
            return new CompilerResponseDTO(
                    evaluationResponse.getRuntimeOutput(),
                    evaluationResponse.getRuntimeError(),
                    evaluationResponse.isPassed()
            );

        } catch (Exception e) {

            return new CompilerResponseDTO(
                    "",
                    e.getMessage(),
                    false
            );
        }
    }
}