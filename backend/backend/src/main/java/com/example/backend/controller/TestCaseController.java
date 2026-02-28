package com.example.backend.controller;

import com.example.backend.dto.TestCaseRequestDTO;
import com.example.backend.entity.Question;
import com.example.backend.entity.TestCase;
import com.example.backend.repository.QuestionRepository;
import com.example.backend.repository.TestCaseRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/testcases")
public class TestCaseController {

    private final TestCaseRepository testCaseRepository;
    private final QuestionRepository questionRepository;

    public TestCaseController(TestCaseRepository testCaseRepository,
                              QuestionRepository questionRepository) {
        this.testCaseRepository = testCaseRepository;
        this.questionRepository = questionRepository;
    }

    @PostMapping
    public ResponseEntity<?> createTestCase(@RequestBody TestCaseRequestDTO request) {

        Question question = questionRepository.findById(request.getQuestionId())
                .orElseThrow(() -> new RuntimeException("Question not found"));

        TestCase testCase = new TestCase();
        testCase.setQuestion(question);
        testCase.setInput(request.getInput());
        testCase.setExpectedOutput(request.getExpectedOutput());

        testCaseRepository.save(testCase);

        return ResponseEntity.ok("Test case added successfully");
    }
}