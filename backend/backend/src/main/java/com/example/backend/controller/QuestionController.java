// package com.example.backend.controller;

// import com.example.backend.entity.Question;
// import com.example.backend.repository.QuestionRepository;
// import org.springframework.web.bind.annotation.*;

// @RestController
// @RequestMapping("/questions")
// public class QuestionController {

//     private final QuestionRepository questionRepository;

//     public QuestionController(QuestionRepository questionRepository) {
//         this.questionRepository = questionRepository;
//     }

//     // ✅ Create Question
//     @PostMapping
//     public Question createQuestion(@RequestBody Question question) {
//         return questionRepository.save(question);
//     }

//     // ✅ Get All Questions
//     @GetMapping
//     public Iterable<Question> getAllQuestions() {
//         return questionRepository.findAll();
//     }
// }

package com.example.backend.controller;

import com.example.backend.entity.Concept;
import com.example.backend.entity.Question;
import com.example.backend.repository.ConceptRepository;
import com.example.backend.repository.QuestionRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/questions")
@CrossOrigin
public class QuestionController {

    private final QuestionRepository questionRepository;
    private final ConceptRepository conceptRepository;

    // ✅ Inject BOTH repositories
    public QuestionController(QuestionRepository questionRepository,
                              ConceptRepository conceptRepository) {
        this.questionRepository = questionRepository;
        this.conceptRepository = conceptRepository;
    }

    // ✅ Create Question
    @PostMapping
    public Question createQuestion(@RequestBody Question question) {
        return questionRepository.save(question);
    }

    // ✅ Get All Questions
    @GetMapping
    public List<Question> getAllQuestions() {
        return questionRepository.findAll();
    }

    // ✅ Get Questions By Concept ID
    @GetMapping("/concept/{conceptId}")
    public List<Question> getQuestionsByConcept(@PathVariable Long conceptId) {

        Concept concept = conceptRepository.findById(conceptId)
                .orElseThrow(() -> new RuntimeException("Concept not found"));

        return questionRepository.findByConcept(concept);
    }

    // ✅ Get Single Question By ID (for Solve page)
    @GetMapping("/{id}")
    public Question getQuestionById(@PathVariable Long id) {
        return questionRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Question not found"));
    }
}