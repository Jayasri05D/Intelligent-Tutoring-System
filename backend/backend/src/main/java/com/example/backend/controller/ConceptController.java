package com.example.backend.controller;

import com.example.backend.entity.Concept;
import com.example.backend.repository.ConceptRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/concepts")
@CrossOrigin
public class ConceptController {

    private final ConceptRepository conceptRepository;

    public ConceptController(ConceptRepository conceptRepository) {
        this.conceptRepository = conceptRepository;
    }

    // ✅ Get all concepts (for homepage)
    @GetMapping
    public List<Concept> getAllConcepts() {
        return conceptRepository.findAll();
    }

    // ✅ Create new concept (Admin use)
    @PostMapping
    public Concept createConcept(@RequestBody Concept concept) {
        return conceptRepository.save(concept);
    }

    // ✅ Get concept by id
    @GetMapping("/{id}")
    public Concept getConceptById(@PathVariable Long id) {
        return conceptRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Concept not found"));
    }

    // ✅ Delete concept
    @DeleteMapping("/{id}")
    public void deleteConcept(@PathVariable Long id) {
        conceptRepository.deleteById(id);
    }
}