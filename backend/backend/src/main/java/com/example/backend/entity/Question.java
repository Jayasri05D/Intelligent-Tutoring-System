// package com.example.backend.entity;

// import jakarta.persistence.*;

// @Entity
// public class Question {

//     @Id
//     @GeneratedValue(strategy = GenerationType.IDENTITY)
//     private Long id;

//     private String title;

//     @Column(length = 2000)
//     private String description;

//     private String difficulty_level;

//     public String getDifficulty_level() {
//         return difficulty_level;
//     }

//     public void setDifficulty_level(String difficulty_level) {
//         this.difficulty_level = difficulty_level;
//     }

//     // ✅ Store concept as plain text
//     @ManyToOne
// @JoinColumn(name = "concept_id")
//     private Concept concept;

//     // Getters & Setters

//     public Long getId() {
//         return id;
//     }

//     public void setId(Long id) {
//         this.id = id;
//     }

//     public String getTitle() {
//         return title;
//     }

//     public void setTitle(String title) {
//         this.title = title;
//     }

//     public String getDescription() {
//         return description;
//     }

//     public void setDescription(String description) {
//         this.description = description;
//     }

//     // public String getDifficulty() {
//     //     return difficulty_level;
//     // }

//     // public void setDifficulty(String difficulty) {
//     //     this.difficulty_level = difficulty;
//     // }

//     public Concept getConcept() {
//         return concept;
//     }

//     public void setConcept(Concept concept) {
//         this.concept = concept;
//     }
// }

package com.example.backend.entity;

import jakarta.persistence.*;

@Entity
public class Question {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    @Column(length = 2000)
    private String description;

    private String difficultyLevel;

    @ManyToOne
    @JoinColumn(name = "concept_id")
    private Concept concept;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getDifficultyLevel() {
        return difficultyLevel;
    }

    public void setDifficultyLevel(String difficultyLevel) {
        this.difficultyLevel = difficultyLevel;
    }

    public Concept getConcept() {
        return concept;
    }

    public void setConcept(Concept concept) {
        this.concept = concept;
    }
}