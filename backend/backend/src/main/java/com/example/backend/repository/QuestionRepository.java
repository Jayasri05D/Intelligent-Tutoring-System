package com.example.backend.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.backend.entity.Concept;
import com.example.backend.entity.Question;

public interface QuestionRepository extends JpaRepository<Question, Long> {
   List<Question> findByConceptId(Long conceptId);
      List<Question> findByConcept(Concept concept);
}