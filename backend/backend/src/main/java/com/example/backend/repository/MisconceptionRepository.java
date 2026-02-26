package com.example.backend.repository;
import com.example.backend.entity.Misconception;
import org.springframework.data.jpa.repository.JpaRepository;
public interface MisconceptionRepository  extends JpaRepository<Misconception, Long> {
    
}
