package com.example.backend.service;

import com.example.backend.dto.*;
import com.example.backend.entity.*;
import com.example.backend.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import java.io.*;
import java.nio.file.Files;
import java.util.concurrent.TimeUnit;

@Service
public class SubmissionService {

    private final WebClient webClient;
    private final StudentRepository studentRepository;
    private final SubmissionRepository submissionRepository;
    private final MisconceptionRepository misconceptionRepository;

    public SubmissionService(WebClient webClient,
StudentRepository studentRepository,
SubmissionRepository submissionRepository,
        MisconceptionRepository misconceptionRepository) {
        this.webClient = webClient;
        this.studentRepository = studentRepository;
        this.submissionRepository = submissionRepository;
        this.misconceptionRepository = misconceptionRepository;
    }

    public AnalyzeResponseDTO analyzeAndSave(CodeRequest requestDTO) {

        // 1️⃣ Call FastAPI
        AnalyzeResponseDTO response = webClient.post()
                .uri("/analyze")
                .bodyValue(requestDTO)
                .retrieve()
                .bodyToMono(AnalyzeResponseDTO.class)
                .block();

        // 2️⃣ Fetch Student
        Student student = studentRepository.findById(requestDTO.getStudentId())
                .orElseThrow(() -> new RuntimeException("Student not found"));

        // 3️⃣ Save Submission
        Submission submission = new Submission();
        submission.setCodeText(requestDTO.getCode());
        submission.setLanguage(requestDTO.getLanguage());
        submission.setHasSyntaxError(response.isHas_syntax_error());
        submission.setStudent(student);

        Submission savedSubmission = submissionRepository.save(submission);

        // 4️⃣ Save Misconceptions
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
    public CompilerResponseDTO runCode(CodeRequest request) {

    String outputText = "";
    String errorText = "";

    try {
        // 1️⃣ Create temporary Python file
        File tempFile = File.createTempFile("student_code_", ".py");
        Files.write(tempFile.toPath(), request.getCode().getBytes());

        // 2️⃣ Execute Python file
        ProcessBuilder processBuilder =
                new ProcessBuilder("python", tempFile.getAbsolutePath());

        processBuilder.redirectErrorStream(false);
        Process process = processBuilder.start();

        // 3️⃣ Timeout protection (important!)
        boolean finished = process.waitFor(5, TimeUnit.SECONDS);
        if (!finished) {
            process.destroy();
            return new CompilerResponseDTO(
                    "",
                    "Execution timed out (Possible infinite loop)"
            );
        }

        // 4️⃣ Capture standard output
        BufferedReader outputReader =
                new BufferedReader(
                        new InputStreamReader(process.getInputStream()));

        StringBuilder outputBuilder = new StringBuilder();
        String line;
        while ((line = outputReader.readLine()) != null) {
            outputBuilder.append(line).append("\n");
        }

        // 5️⃣ Capture error output
        BufferedReader errorReader =
                new BufferedReader(
                        new InputStreamReader(process.getErrorStream()));

        StringBuilder errorBuilder = new StringBuilder();
        while ((line = errorReader.readLine()) != null) {
            errorBuilder.append(line).append("\n");
        }

        outputText = outputBuilder.toString();
        errorText = errorBuilder.toString();

        // 6️⃣ Delete temp file
        tempFile.delete();

    } catch (Exception e) {
        errorText = e.getMessage();
    }

    return new CompilerResponseDTO(outputText, errorText);
}
}