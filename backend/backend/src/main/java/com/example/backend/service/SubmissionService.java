// package com.example.backend.service;

// import com.example.backend.dto.*;
// import com.example.backend.entity.*;
// import com.example.backend.repository.*;
// import org.springframework.stereotype.Service;
// import org.springframework.web.reactive.function.client.WebClient;
// import java.io.*;
// import java.nio.file.Files;
// import java.util.concurrent.TimeUnit;

// @Service
// public class SubmissionService {

//     private final WebClient webClient;
//     private final StudentRepository studentRepository;
//     private final SubmissionRepository submissionRepository;
//     private final MisconceptionRepository misconceptionRepository;

//     public SubmissionService(WebClient webClient,
// StudentRepository studentRepository,
// SubmissionRepository submissionRepository,
//         MisconceptionRepository misconceptionRepository) {
//         this.webClient = webClient;
//         this.studentRepository = studentRepository;
//         this.submissionRepository = submissionRepository;
//         this.misconceptionRepository = misconceptionRepository;
//     }

//     public AnalyzeResponseDTO analyzeAndSave(CodeRequest requestDTO) {

//         // 1️⃣ Call FastAPI
//         AnalyzeResponseDTO response = webClient.post()
//                 .uri("/analyze")
//                 .bodyValue(requestDTO)
//                 .retrieve()
//                 .bodyToMono(AnalyzeResponseDTO.class)
//                 .block();

//         // 2️⃣ Fetch Student
//         Student student = studentRepository.findById(requestDTO.getStudentId())
//                 .orElseThrow(() -> new RuntimeException("Student not found"));

//         // 3️⃣ Save Submission
//         Submission submission = new Submission();
//         submission.setCodeText(requestDTO.getCode());
//         submission.setLanguage(requestDTO.getLanguage());
//         submission.setHasSyntaxError(response.isHas_syntax_error());
//         submission.setStudent(student);

//         Submission savedSubmission = submissionRepository.save(submission);

//         // 4️⃣ Save Misconceptions
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
//     public CompilerResponseDTO runCode(CodeRequest request) {

//     String outputText = "";
//     String errorText = "";

//     try {
//         // 1️⃣ Create temporary Python file
//         File tempFile = File.createTempFile("student_code_", ".py");
//         Files.write(tempFile.toPath(), request.getCode().getBytes());

//         // 2️⃣ Execute Python file
//         ProcessBuilder processBuilder =
//                 new ProcessBuilder("python", tempFile.getAbsolutePath());

//         processBuilder.redirectErrorStream(false);
//         Process process = processBuilder.start();

//         // 3️⃣ Timeout protection (important!)
//         boolean finished = process.waitFor(5, TimeUnit.SECONDS);
//         if (!finished) {
//             process.destroy();
//             return new CompilerResponseDTO(
//                     "",
//                     "Execution timed out (Possible infinite loop)"
//             );
//         }

//         // 4️⃣ Capture standard output
//         BufferedReader outputReader =
//                 new BufferedReader(
//                         new InputStreamReader(process.getInputStream()));

//         StringBuilder outputBuilder = new StringBuilder();
//         String line;
//         while ((line = outputReader.readLine()) != null) {
//             outputBuilder.append(line).append("\n");
//         }

//         // 5️⃣ Capture error output
//         BufferedReader errorReader =
//                 new BufferedReader(
//                         new InputStreamReader(process.getErrorStream()));

//         StringBuilder errorBuilder = new StringBuilder();
//         while ((line = errorReader.readLine()) != null) {
//             errorBuilder.append(line).append("\n");
//         }

//         outputText = outputBuilder.toString();
//         errorText = errorBuilder.toString();

//         // 6️⃣ Delete temp file
//         tempFile.delete();

//     } catch (Exception e) {
//         errorText = e.getMessage();
//     }

//     return new CompilerResponseDTO(outputText, errorText);
// }
// }

package com.example.backend.service;

import com.example.backend.dto.*;
import com.example.backend.entity.*;
import com.example.backend.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.io.*;
import java.nio.file.Files;
import java.util.List;
import java.util.concurrent.TimeUnit;

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
    // 🧠 1️⃣ ANALYZE ONLY (AI Semantic Analysis)
    // =========================================================
    public AnalyzeResponseDTO analyzeAndSave(CodeRequest request) {

        // 1️⃣ Call FastAPI
        AnalyzeResponseDTO response = webClient.post()
                .uri("/analyze")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(AnalyzeResponseDTO.class)
                .block();

        // 2️⃣ Fetch student
        Student student = studentRepository.findById(request.getStudentId())
                .orElseThrow(() -> new RuntimeException("Student not found"));

        // 3️⃣ Save submission (no question, no pass/fail)
        Submission submission = new Submission();
        submission.setCodeText(request.getCode());
        submission.setLanguage(request.getLanguage());
        submission.setHasSyntaxError(response.isHas_syntax_error());
        submission.setPassed(false); // analyze mode
        submission.setStudent(student);

        Submission savedSubmission = submissionRepository.save(submission);

        // 4️⃣ Save misconceptions
        if (response.getViolations() != null) {
            for (ViolationDTO v : response.getViolations()) {

                Misconception m = new Misconception();
                m.setRuleId(v.getRuleId());
                m.setConcept(v.getConcept());
                m.setLineNumber(v.getLine());
                m.setConfidence(v.getConfidence());
                m.setSubmission(savedSubmission);

                misconceptionRepository.save(m);
            }
        }

        return response;
    }


    // =========================================================
    // 🚀 2️⃣ FULL SUBMISSION (Run + Validate + Analyze)
    // =========================================================
//     public CompilerResponseDTO submitCode(Long questionId, CodeRequest request) {

//         String runtimeOutput = "";
//         String runtimeError = "";
//         boolean allPassed = true;

//         try {
//             Student student = studentRepository.findById(request.getStudentId())
//                     .orElseThrow(() -> new RuntimeException("Student not found"));

//             Question question = questionRepository.findById(questionId)
//                     .orElseThrow(() -> new RuntimeException("Question not found"));

//             List<TestCase> testCases = testCaseRepository.findByQuestionId(questionId);
//             if (testCases.isEmpty()) {
//     return new CompilerResponseDTO(
//             "",
//             "No test cases found for this question.",
//             false
//     );
// }

//             File tempFile = File.createTempFile("student_code_", ".py");
//             Files.write(tempFile.toPath(), request.getCode().getBytes());

//            for (TestCase testCase : testCases) {

//     ProcessBuilder pb = new ProcessBuilder("python", tempFile.getAbsolutePath());
//     Process process = pb.start();

//     // 🔥 SEND INPUT TO PYTHON
//     BufferedWriter writer =
//             new BufferedWriter(new OutputStreamWriter(process.getOutputStream()));
//     writer.write(testCase.getInput());
//     writer.newLine();
//     writer.flush();
//     writer.close();

//     boolean finished = process.waitFor(5, TimeUnit.SECONDS);
//     if (!finished) {
//         process.destroy();
//         runtimeError = "Execution timed out";
//         allPassed = false;
//         break;
//     }

//     // 🔥 READ OUTPUT
//     BufferedReader outputReader =
//             new BufferedReader(new InputStreamReader(process.getInputStream()));

//     StringBuilder outputBuilder = new StringBuilder();
//     String line;
//     while ((line = outputReader.readLine()) != null) {
//         outputBuilder.append(line);
//     }

//     runtimeOutput = outputBuilder.toString().trim();

//     // 🔥 READ ERROR STREAM
//     BufferedReader errorReader =
//             new BufferedReader(new InputStreamReader(process.getErrorStream()));

//     StringBuilder errorBuilder = new StringBuilder();
//     while ((line = errorReader.readLine()) != null) {
//         errorBuilder.append(line);
//     }

//     runtimeError = errorBuilder.toString().trim();

//     if (!runtimeOutput.equals(testCase.getExpectedOutput().trim())) {
//         allPassed = false;
//     }
// }
//             tempFile.delete();

//             // Call AI
//             AnalyzeResponseDTO analyzeResponse = webClient.post()
//                     .uri("/analyze")
//                     .bodyValue(request)
//                     .retrieve()
//                     .bodyToMono(AnalyzeResponseDTO.class)
//                     .block();

//             // Save submission
//             Submission submission = new Submission();
//             submission.setCodeText(request.getCode());
//             submission.setLanguage(request.getLanguage());
//             submission.setHasSyntaxError(analyzeResponse.isHas_syntax_error());
//             submission.setPassed(allPassed);
//             submission.setRuntimeOutput(runtimeOutput);
//             submission.setRuntimeError(runtimeError);
//             submission.setStudent(student);
//             submission.setQuestion(question);

//             Submission savedSubmission = submissionRepository.save(submission);

//             // Save misconceptions
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

//         } catch (Exception e) {
//             runtimeError = e.getMessage();
//         }
       

//         return new CompilerResponseDTO(runtimeOutput, runtimeError, allPassed);
//     }
public CompilerResponseDTO submitCode(Long questionId, CodeRequest request) {

    String runtimeError = "";
    boolean allPassed = true;
    StringBuilder finalOutput = new StringBuilder();

    File tempFile = null;

    try {
        // ============================
        // 1️⃣ Fetch Student & Question
        // ============================
        Student student = studentRepository.findById(request.getStudentId())
                .orElseThrow(() -> new RuntimeException("Student not found"));

        Question question = questionRepository.findById(questionId)
                .orElseThrow(() -> new RuntimeException("Question not found"));

        List<TestCase> testCases = testCaseRepository.findByQuestionId(questionId);
        if (testCases.isEmpty()) {
            return new CompilerResponseDTO(
                    "",
                    "No test cases found for this question.",
                    false
            );
        }

        // ============================
        // 2️⃣ Create Temporary Python File
        // ============================
        tempFile = File.createTempFile("student_code_", ".py");
        Files.write(tempFile.toPath(), request.getCode().getBytes());

        // ============================
        // 3️⃣ Execute For Each Test Case
        // ============================
        for (TestCase testCase : testCases) {

            ProcessBuilder pb = new ProcessBuilder("python", tempFile.getAbsolutePath());
            Process process = pb.start();

            // Send input
            try (BufferedWriter writer = new BufferedWriter(
                    new OutputStreamWriter(process.getOutputStream()))) {
                writer.write(testCase.getInput());
                writer.newLine();
                writer.flush();
            }

            // Wait max 5 seconds
            boolean finished = process.waitFor(5, TimeUnit.SECONDS);
            if (!finished) {
                process.destroyForcibly();
                runtimeError = "Execution timed out";
                allPassed = false;
                break;
            }

            // Read Output
            String currentOutput;
            try (BufferedReader outputReader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {

                StringBuilder outputBuilder = new StringBuilder();
                String line;
                while ((line = outputReader.readLine()) != null) {
                    outputBuilder.append(line);
                }

                currentOutput = outputBuilder.toString().trim();
            }

            // Read Error
            try (BufferedReader errorReader = new BufferedReader(
                    new InputStreamReader(process.getErrorStream()))) {

                StringBuilder errorBuilder = new StringBuilder();
                String line;
                while ((line = errorReader.readLine()) != null) {
                    errorBuilder.append(line);
                }

                runtimeError = errorBuilder.toString().trim();
            }

            // If runtime error exists → stop checking further
            if (!runtimeError.isEmpty()) {
                allPassed = false;
                break;
            }

            // Compare with expected output
            if (!currentOutput.equals(testCase.getExpectedOutput().trim())) {
                allPassed = false;
            }

            // Append to final output
            finalOutput.append(currentOutput).append("\n");
        }

        // ============================
        // 4️⃣ AI Analysis Call
        // ============================
        AnalyzeResponseDTO analyzeResponse = webClient.post()
                .uri("/analyze")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(AnalyzeResponseDTO.class)
                .block();

        // ============================
        // 5️⃣ Save Submission
        // ============================
        Submission submission = new Submission();
        submission.setCodeText(request.getCode());
        submission.setLanguage(request.getLanguage());
        submission.setHasSyntaxError(analyzeResponse.isHas_syntax_error());
        submission.setPassed(allPassed);
        submission.setRuntimeOutput(finalOutput.toString().trim());
        submission.setRuntimeError(runtimeError);
        submission.setStudent(student);
        submission.setQuestion(question);

        Submission savedSubmission = submissionRepository.save(submission);

        // Save misconceptions
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

    } catch (Exception e) {
        runtimeError = e.getMessage();
        allPassed = false;
    } finally {
        if (tempFile != null && tempFile.exists()) {
            tempFile.delete();
        }
    }

    return new CompilerResponseDTO(
            finalOutput.toString().trim(),
            runtimeError,
            allPassed
    );
}
}