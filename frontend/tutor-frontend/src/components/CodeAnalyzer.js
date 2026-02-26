// src/CodeAnalyzer.js
import React, { useState } from "react";

function CodeAnalyzer() {
  const [studentId, setStudentId] = useState("");
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://localhost:8080/api/submissions/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          studentId: parseInt(studentId),
          language: "python",
          code: code
        })
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
      alert("Something went wrong");
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h2>Intelligent Code Tutor</h2>

      <div>
        <label>Student ID:</label><br />
        <input
          type="number"
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
        />
      </div>

      <br />

      <div>
        <label>Python Code:</label><br />
        <textarea
          rows="10"
          cols="60"
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
      </div>

      <br />

      <button onClick={handleAnalyze}>
        {loading ? "Analyzing..." : "Analyze Code"}
      </button>

      <hr />

      {result && (
        <div>
          <h3>Analysis Result</h3>
          <p><strong>Syntax Error:</strong> {result.has_syntax_error ? "Yes" : "No"}</p>

          {result.violations && result.violations.length > 0 ? (
            result.violations.map((v, index) => (
              <div key={index} style={{ border: "1px solid red", padding: "10px", margin: "10px 0" }}>
                <p><strong>Rule:</strong> {v.rule_id}</p>
                <p><strong>Concept:</strong> {v.concept}</p>
                <p><strong>Line:</strong> {v.line}</p>
                <p><strong>Confidence:</strong> {v.confidence}</p>
              </div>
            ))
          ) : (
            <p>No violations detected 🎉</p>
          )}
        </div>
      )}
    </div>
  );
}

export default CodeAnalyzer;