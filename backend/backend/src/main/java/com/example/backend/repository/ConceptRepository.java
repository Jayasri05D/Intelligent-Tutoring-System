package com.example.backend.repository;


import org.springframework.data.jpa.repository.JpaRepository;

import com.example.backend.entity.Concept;


public interface ConceptRepository extends JpaRepository<Concept, Long> {}



