package com.example.backend.service;

import com.example.backend.dto.*;
import com.example.backend.entity.*;
import com.example.backend.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

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
                m.setRuleId(v.getRule_id());
                m.setConcept(v.getConcept());
                m.setLineNumber(v.getLine());
                m.setConfidence(v.getConfidence());
                m.setSubmission(savedSubmission);

                misconceptionRepository.save(m);
            }
        }

        return response;
    }
}