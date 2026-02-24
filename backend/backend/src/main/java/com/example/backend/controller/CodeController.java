package com.example.backend.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.example.backend.dto.CodeRequest;

@RestController
@RequestMapping("/api")
public class CodeController {
    @Autowired
private RestTemplate restTemplate;

@PostMapping("/analyze")
public ResponseEntity<?> analyze(@RequestBody CodeRequest request) {

    String pythonUrl = "http://localhost:8000/analyze";

    ResponseEntity<String> response =
        restTemplate.postForEntity(pythonUrl, request, String.class);

    return ResponseEntity.ok(response.getBody());
}
}
