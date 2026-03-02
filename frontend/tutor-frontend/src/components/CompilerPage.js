

// export default CompilerPage;

// import React, { useState, useEffect } from "react";
// import { useParams } from "react-router-dom";

// function CompilerPage() {
//   const { questionId } = useParams();

//   const [question, setQuestion] = useState(null);
//   const [code, setCode] = useState("");
//   const [runtimeOutput, setRuntimeOutput] = useState("");
//   const [analysisResult, setAnalysisResult] = useState(null);
//   const [loading, setLoading] = useState(false);

//   useEffect(() => {
//     const fetchQuestion = async () => {
//       try {
//         const response = await fetch(
//           `http://localhost:8080/api/questions/${questionId}`
//         );
//         const data = await response.json();
//         setQuestion(data);
//       } catch (err) {
//         console.error("Error fetching question:", err);
//       }
//     };
//     fetchQuestion();
//   }, [questionId]);

//   const handleRun = async () => {
//     setLoading(true);
//     setRuntimeOutput("");
//     setAnalysisResult(null);

//     try {
//       const response = await fetch(
//         `http://localhost:8080/api/submissions/run/${questionId}`,
//         {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ studentId: 1, language: "python", code }),
//         }
//       );
//       const data = await response.json();
//       if (data.length > 0) {
//         const first = data[0];
//         setRuntimeOutput(first.actualOutput || first.runtime_error || "No output");
//       }
//     } catch (err) {
//       console.error(err);
//       setRuntimeOutput("Error running code.");
//     }

//     setLoading(false);
//   };

//   const handleAnalyze = async () => {
//     setLoading(true);
//     setAnalysisResult(null);

//     try {
//       const response = await fetch(
//         "http://localhost:8080/api/submissions/analyze",
//         {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ studentId: 1, questionId, language: "python", code }),
//         }
//       );
//       const data = await response.json();
//       setAnalysisResult(data);
//     } catch (err) {
//       console.error("Analyze error:", err);
//     }

//     setLoading(false);
//   };

//   // ================= STYLES =================
//   const styles = {
//     container: { display: "flex", height: "100vh", fontFamily: "Arial, sans-serif", background: "#f4f4f4" },
//     leftPane: {
//       width: "40%",
//       padding: "25px",
//       borderRight: "1px solid #ddd",
//       overflowY: "auto",
//       background: "#fff"
//     },
//     rightPane: {
//       width: "60%",
//       padding: "25px",
//       display: "flex",
//       flexDirection: "column",
//       overflowY: "auto"
//     },
//     textarea: {
//       width: "100%",
//       height: "300px",
//       padding: "15px",
//       fontFamily: "monospace",
//       fontSize: "14px",
//       borderRadius: "8px",
//       border: "1px solid #ccc",
//       background: "#f9f9f9",
//       resize: "vertical",
//       boxSizing: "border-box"
//     },
//     button: {
//       padding: "10px 20px",
//       marginRight: "10px",
//       border: "none",
//       borderRadius: "5px",
//       cursor: "pointer",
//       fontWeight: "bold",
//       transition: "all 0.2s ease",
//     },
//     runButton: { background: "#4CAF50", color: "white" },
//     analyzeButton: { background: "#2196F3", color: "white" },
//     buttonHover: { opacity: 0.85 },
//     consoleOutput: {
//       background: "#1e1e1e",
//       color: "#d4d4d4",
//       padding: "15px",
//       marginTop: "20px",
//       borderRadius: "8px",
//       fontFamily: "monospace",
//       maxHeight: "200px",
//       overflowY: "auto"
//     },
//     analysisSection: { marginTop: "30px" },
//     testCaseBox: (passed) => ({
//       border: `2px solid ${passed ? "#4CAF50" : "#f44336"}`,
//       borderRadius: "6px",
//       padding: "15px",
//       marginBottom: "15px",
//       background: passed ? "#f0fff0" : "#fff0f0"
//     }),
//     logicalErrorBox: {
//       border: "2px solid #f44336",
//       borderRadius: "6px",
//       padding: "15px",
//       marginBottom: "15px",
//       background: "#fff5f5"
//     }
//   };

//   return (
//     <div style={styles.container}>
//       {/* LEFT SIDE - QUESTION */}
//       <div style={styles.leftPane}>
//         <h3>Question {questionId}</h3>
//         {question ? (
//           <>
//             <h4>{question.title}</h4>
//             <p>{question.description}</p>
//           </>
//         ) : (
//           <p>Loading...</p>
//         )}
//       </div>

//       {/* RIGHT SIDE - COMPILER */}
//       <div style={styles.rightPane}>
//         <textarea
//           style={styles.textarea}
//           value={code}
//           onChange={(e) => setCode(e.target.value)}
//           placeholder="Write your Python code here..."
//         />

//         <div style={{ marginTop: "15px" }}>
//           <button
//             style={{ ...styles.button, ...styles.runButton }}
//             onClick={handleRun}
//             disabled={loading}
//           >
//             {loading ? "Processing..." : "Run Code"}
//           </button>
//           <button
//             style={{ ...styles.button, ...styles.analyzeButton }}
//             onClick={handleAnalyze}
//             disabled={loading}
//           >
//             {loading ? "Processing..." : "Analyze Code"}
//           </button>
//         </div>

//         {/* ================= CONSOLE OUTPUT ================= */}
//         {runtimeOutput && (
//           <div style={styles.consoleOutput}>
//             <h4 style={{ color: "white" }}>Console Output</h4>
//             <pre>{runtimeOutput}</pre>
//           </div>
//         )}

//         {/* ================= ANALYSIS RESULT ================= */}
//         {analysisResult && (
//           <div style={styles.analysisSection}>
//             <h3>Analysis Result</h3>

//             {analysisResult.test_summary && (
//               <div style={{ marginBottom: "20px" }}>
//                 <h4>Test Summary</h4>
//                 <p>Score: {analysisResult.test_summary.score}</p>
//                 <p>
//                   Passed: {analysisResult.test_summary.passed} / {analysisResult.test_summary.total}
//                 </p>
//               </div>
//             )}

//             {analysisResult.test_results && (
//               <div>
//                 <h4>Test Case Details</h4>
//                 {analysisResult.test_results.map((test, index) => (
//                   <div key={index} style={styles.testCaseBox(test.passed)}>
//                     <p><strong>Input:</strong></p>
//                     <pre>{test.input}</pre>
//                     <p><strong>Expected:</strong> {test.expected}</p>
//                     <p><strong>Actual:</strong> {test.actual}</p>
//                     {test.runtime_error && (
//                       <>
//                         <p><strong>Runtime Error:</strong></p>
//                         <pre style={{ color: "red" }}>{test.runtime_error}</pre>
//                       </>
//                     )}
//                     <p><strong>Status:</strong> {test.passed ? "Passed ✅" : "Failed ❌"}</p>
//                   </div>
//                 ))}
//               </div>
//             )}

//             {analysisResult.logical_errors &&
//              analysisResult.logical_errors.length > 0 && (
//               <div style={{ marginTop: "30px" }}>
//                 <h4>Logical Errors Detected</h4>
//                 {analysisResult.logical_errors.map((err, index) => (
//                   <div key={index} style={styles.logicalErrorBox}>
//                     <p><strong>Error:</strong> {err.what}</p>
//                     <p><strong>Where:</strong> {err.where}</p>
//                     <p><strong>Why:</strong> {err.why}</p>
//                     <p><strong>Hint:</strong> {err.hint}</p>
//                     <p><strong>Confidence:</strong> {err.confidence}</p>
//                     {err.code_snippet && (
//                       <>
//                         <p><strong>Code Snippet:</strong></p>
//                         <pre>{err.code_snippet}</pre>
//                       </>
//                     )}
//                   </div>
//                 ))}
//               </div>
//             )}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// export default CompilerPage;

import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

function CompilerPage() {
  const { questionId } = useParams();

  const [question, setQuestion] = useState(null);
  const [code, setCode] = useState("");
  const [runtimeOutput, setRuntimeOutput] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("code"); // "code" or "output"

  useEffect(() => {
    const fetchQuestion = async () => {
      try {
        const response = await fetch(`http://localhost:8080/api/questions/${questionId}`);
        const data = await response.json();
        setQuestion(data);
      } catch (err) {
        console.error("Error fetching question:", err);
      }
    };
    fetchQuestion();
  }, [questionId]);

  const handleRun = async () => {
    setLoading(true);
    setRuntimeOutput("");
    setAnalysisResult(null);
    try {
      const response = await fetch(
        `http://localhost:8080/api/submissions/run/${questionId}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ studentId: 1, language: "python", code }),
        }
      );
      const data = await response.json();
      if (data.length > 0) {
        const first = data[0];
        setRuntimeOutput(first.actualOutput || first.runtime_error || "No output");
        setActiveTab("output");
      }
    } catch (err) {
      console.error(err);
      setRuntimeOutput("Error running code.");
      setActiveTab("output");
    }
    setLoading(false);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setAnalysisResult(null);
    try {
      const response = await fetch("http://localhost:8080/api/submissions/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ studentId: 1, questionId, language: "python", code }),
      });
      const data = await response.json();
      setAnalysisResult(data);
      setActiveTab("output");
    } catch (err) {
      console.error("Analyze error:", err);
    }
    setLoading(false);
  };

  const styles = {
    container: { display: "flex", height: "100vh", fontFamily: "Consolas, monospace", background: "#1e1e1e", color: "#ddd" },
    leftPane: { width: "35%", padding: "20px", borderRight: "1px solid #333", overflowY: "auto" },
    rightPane: { width: "65%", display: "flex", flexDirection: "column" },
    editorContainer: { display: "flex", flexDirection: "column", height: "100%" },
    tabs: { display: "flex", borderBottom: "1px solid #333" },
    tab: (active) => ({
      padding: "10px 20px",
      cursor: "pointer",
      background: active ? "#252526" : "#1e1e1e",
      borderBottom: active ? "3px solid #007acc" : "none",
      color: "#ddd",
      fontWeight: active ? "bold" : "normal"
    }),
    textarea: {
      flexGrow: 1,
      padding: "15px",
      fontFamily: "monospace",
      fontSize: "14px",
      background: "#1e1e1e",
      color: "#d4d4d4",
      border: "none",
      outline: "none",
      resize: "none"
    },
    buttonContainer: { marginTop: "10px", display: "flex", gap: "10px" },
    button: {
      padding: "8px 16px",
      border: "none",
      borderRadius: "4px",
      cursor: "pointer",
      fontWeight: "bold",
      transition: "all 0.2s ease",
    },
    runButton: { background: "#0e639c", color: "#fff" },
    analyzeButton: { background: "#007acc", color: "#fff" },
    consoleOutput: {
      flexGrow: 1,
      background: "#1e1e1e",
      color: "#d4d4d4",
      padding: "15px",
      overflowY: "auto"
    },
    analysisSection: { marginTop: "20px" },
    testCaseBox: (passed) => ({
      border: `1px solid ${passed ? "#4caf50" : "#f44336"}`,
      borderRadius: "5px",
      padding: "10px",
      marginBottom: "10px",
      background: passed ? "#223322" : "#331111"
    }),
    logicalErrorBox: {
      border: "1px solid #f44336",
      borderRadius: "5px",
      padding: "10px",
      marginBottom: "10px",
      background: "#330000"
    }
  };

  return (
    <div style={styles.container}>
      {/* LEFT SIDE */}
      <div style={styles.leftPane}>
        <h3>Question {questionId}</h3>
        {question ? (
          <>
            <h4>{question.title}</h4>
            <p>{question.description}</p>
          </>
        ) : (
          <p>Loading...</p>
        )}
      </div>

      {/* RIGHT SIDE */}
      <div style={styles.rightPane}>
        {/* TABS */}
        <div style={styles.tabs}>
          <div style={styles.tab(activeTab === "code")} onClick={() => setActiveTab("code")}>Code</div>
          <div style={styles.tab(activeTab === "output")} onClick={() => setActiveTab("output")}>Output</div>
        </div>

        <div style={styles.editorContainer}>
          {activeTab === "code" && (
            <>
              <textarea
                style={styles.textarea}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Write your Python code here..."
              />
              <div style={styles.buttonContainer}>
                <button style={{ ...styles.button, ...styles.runButton }} onClick={handleRun} disabled={loading}>
                  {loading ? "Running..." : "Run Code"}
                </button>
                <button style={{ ...styles.button, ...styles.analyzeButton }} onClick={handleAnalyze} disabled={loading}>
                  {loading ? "Analyzing..." : "Analyze Code"}
                </button>
              </div>
            </>
          )}

          {activeTab === "output" && (
            <div style={styles.consoleOutput}>
              <h4>Console Output</h4>
              <pre>{runtimeOutput || "No output yet"}</pre>

              {analysisResult && (
                <div style={styles.analysisSection}>
                  {analysisResult.test_summary && (
                    <div>
                      <h4>Test Summary</h4>
                      <p>Score: {analysisResult.test_summary.score}</p>
                      <p>Passed: {analysisResult.test_summary.passed} / {analysisResult.test_summary.total}</p>
                    </div>
                  )}

                  {analysisResult.test_results && (
                    <div>
                      <h4>Test Cases</h4>
                      {analysisResult.test_results.map((test, i) => (
                        <div key={i} style={styles.testCaseBox(test.passed)}>
                          <p><strong>Input:</strong> {test.input}</p>
                          <p><strong>Expected:</strong> {test.expected}</p>
                          <p><strong>Actual:</strong> {test.actual}</p>
                          {test.runtime_error && <pre style={{ color: "#f44336" }}>{test.runtime_error}</pre>}
                          <p>Status: {test.passed ? "Passed ✅" : "Failed ❌"}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {analysisResult.logical_errors && analysisResult.logical_errors.length > 0 && (
                    <div>
                      <h4>Logical Errors</h4>
                      {analysisResult.logical_errors.map((err, i) => (
                        <div key={i} style={styles.logicalErrorBox}>
                          <p><strong>Error:</strong> {err.what}</p>
                          <p><strong>Where:</strong> {err.where}</p>
                          <p><strong>Why:</strong> {err.why}</p>
                          <p><strong>Hint:</strong> {err.hint}</p>
                          <p><strong>Confidence:</strong> {err.confidence}</p>
                          {err.code_snippet && <pre>{err.code_snippet}</pre>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CompilerPage;