📘 Explainable AI Tutor for Programming Misconceptions

Detecting misconceptions, not just mistakes.

📌 Overview

This project presents an Explainable AI-driven Intelligent Tutoring System designed to detect semantic errors and underlying conceptual misconceptions in novice programmers’ code.

Unlike traditional auto-graders that only validate outputs against test cases, this system:

Identifies logical and conceptual misunderstandings

Maps errors to programming concepts

Generates structured, explainable feedback

Provides personalized learning support

The goal is to bridge the gap between automated feedback and true conceptual understanding in programming education.

🎯 Problem Statement

Most AI-based coding assistants and auto-grading platforms focus on:

Syntax correction

Output validation

Direct solution generation

However, they fail to:

Identify why a student made a mistake

Detect recurring misconceptions

Provide transparent reasoning

Offer structured conceptual repair

This system addresses those gaps using Explainable AI and semantic analysis.

🧠 Key Features
✅ Semantic Error Detection

Test case validation

Logical error detection

AST-based structural analysis

✅ Misconception Mapping

Concept graph for programming topics

Classification of common misconception patterns

Recurring error tracking

✅ Explainable Feedback Generation

Structured feedback includes:

Location of error

Violated principle

Concept explanation

Analogy-based clarification

Learning resource reference

✅ Personalization

Tracks student performance history

Adapts explanations based on weak concepts

Identifies repeated misconception trends

🏗️ System Architecture

Code Submission Interface (Frontend)

Backend Processing Layer

Syntax validation

Semantic analysis

Misconception Classification Module

Explainable Feedback Generator (LLM + RAG)

Student Modeling & Personalization Engine

🛠️ Technologies Used
Frontend

React.js

Monaco Code Editor

Backend

Spring Boot

REST APIs

MySQL / MongoDB

AI & NLP Layer

Python microservice

Hugging Face LLMs

Tree-sitter (AST parsing)

FAISS / ChromaDB (Retrieval-Augmented Generation)

spaCy (optional NLP processing)

Dev Tools

Docker

GitHub

Postman

🔍 How It Works

Student submits code.

System validates execution and analyzes structure.

Detected errors are mapped to a predefined concept graph.

LLM generates structured, explainable feedback.

Student model updates recurring misconception profile.

Future explanations adapt based on learning history.

📊 Research Contribution

This project contributes to:

Artificial Intelligence in Education (AIED)

Explainable AI (XAI) for learning systems

Semantic misconception detection in programming

Personalized conceptual feedback generation

Unlike constraint-only systems, this framework integrates:

Semantic reasoning

Concept mapping

Structured explanation modeling

Personalization mechanisms

📚 Domain

Artificial Intelligence in Education (AIED)
Explainable AI (XAI)
Intelligent Tutoring Systems (ITS)
