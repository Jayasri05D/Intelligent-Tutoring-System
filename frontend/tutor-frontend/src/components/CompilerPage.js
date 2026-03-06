

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

// import React, { useState, useEffect } from "react";
// import { useParams } from "react-router-dom";

// function CompilerPage() {
//   const { questionId } = useParams();

//   const [question, setQuestion] = useState(null);
//   const [code, setCode] = useState("");
//   const [runtimeOutput, setRuntimeOutput] = useState("");
//   const [analysisResult, setAnalysisResult] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [activeTab, setActiveTab] = useState("code"); // "code" or "output"

//   useEffect(() => {
//     const fetchQuestion = async () => {
//       try {
//         const response = await fetch(`http://localhost:8080/api/questions/${questionId}`);
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
//         setActiveTab("output");
//       }
//     } catch (err) {
//       console.error(err);
//       setRuntimeOutput("Error running code.");
//       setActiveTab("output");
//     }
//     setLoading(false);
//   };

//   const handleAnalyze = async () => {
//     setLoading(true);
//     setAnalysisResult(null);
//     try {
//       const response = await fetch("http://localhost:8080/api/submissions/analyze", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ studentId: 1, questionId, language: "python", code }),
//       });
//       const data = await response.json();
//       setAnalysisResult(data);
//       setActiveTab("output");
//     } catch (err) {
//       console.error("Analyze error:", err);
//     }
//     setLoading(false);
//   };

//   const styles = {
//     container: { display: "flex", height: "100vh", fontFamily: "Consolas, monospace", background: "#1e1e1e", color: "#ddd" },
//     leftPane: { width: "35%", padding: "20px", borderRight: "1px solid #333", overflowY: "auto" },
//     rightPane: { width: "65%", display: "flex", flexDirection: "column" },
//     editorContainer: { display: "flex", flexDirection: "column", height: "100%" },
//     tabs: { display: "flex", borderBottom: "1px solid #333" },
//     tab: (active) => ({
//       padding: "10px 20px",
//       cursor: "pointer",
//       background: active ? "#252526" : "#1e1e1e",
//       borderBottom: active ? "3px solid #007acc" : "none",
//       color: "#ddd",
//       fontWeight: active ? "bold" : "normal"
//     }),
//     textarea: {
//       flexGrow: 1,
//       padding: "15px",
//       fontFamily: "monospace",
//       fontSize: "14px",
//       background: "#1e1e1e",
//       color: "#d4d4d4",
//       border: "none",
//       outline: "none",
//       resize: "none"
//     },
//     buttonContainer: { marginTop: "10px", display: "flex", gap: "10px" },
//     button: {
//       padding: "8px 16px",
//       border: "none",
//       borderRadius: "4px",
//       cursor: "pointer",
//       fontWeight: "bold",
//       transition: "all 0.2s ease",
//     },
//     runButton: { background: "#0e639c", color: "#fff" },
//     analyzeButton: { background: "#007acc", color: "#fff" },
//     consoleOutput: {
//       flexGrow: 1,
//       background: "#1e1e1e",
//       color: "#d4d4d4",
//       padding: "15px",
//       overflowY: "auto"
//     },
//     analysisSection: { marginTop: "20px" },
//     testCaseBox: (passed) => ({
//       border: `1px solid ${passed ? "#4caf50" : "#f44336"}`,
//       borderRadius: "5px",
//       padding: "10px",
//       marginBottom: "10px",
//       background: passed ? "#223322" : "#331111"
//     }),
//     logicalErrorBox: {
//       border: "1px solid #f44336",
//       borderRadius: "5px",
//       padding: "10px",
//       marginBottom: "10px",
//       background: "#330000"
//     }
//   };

//   return (
//     <div style={styles.container}>
//       {/* LEFT SIDE */}
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

//       {/* RIGHT SIDE */}
//       <div style={styles.rightPane}>
//         {/* TABS */}
//         <div style={styles.tabs}>
//           <div style={styles.tab(activeTab === "code")} onClick={() => setActiveTab("code")}>Code</div>
//           <div style={styles.tab(activeTab === "output")} onClick={() => setActiveTab("output")}>Output</div>
//         </div>

//         <div style={styles.editorContainer}>
//           {activeTab === "code" && (
//             <>
//               <textarea
//                 style={styles.textarea}
//                 value={code}
//                 onChange={(e) => setCode(e.target.value)}
//                 placeholder="Write your Python code here..."
//               />
//               <div style={styles.buttonContainer}>
//                 <button style={{ ...styles.button, ...styles.runButton }} onClick={handleRun} disabled={loading}>
//                   {loading ? "Running..." : "Run Code"}
//                 </button>
//                 <button style={{ ...styles.button, ...styles.analyzeButton }} onClick={handleAnalyze} disabled={loading}>
//                   {loading ? "Analyzing..." : "Analyze Code"}
//                 </button>
//               </div>
//             </>
//           )}

//           {activeTab === "output" && (
//             <div style={styles.consoleOutput}>
//               <h4>Console Output</h4>
//               <pre>{runtimeOutput || "No output yet"}</pre>

//               {analysisResult && (
//                 <div style={styles.analysisSection}>
//                   {analysisResult.test_summary && (
//                     <div>
//                       <h4>Test Summary</h4>
//                       <p>Score: {analysisResult.test_summary.score}</p>
//                       <p>Passed: {analysisResult.test_summary.passed} / {analysisResult.test_summary.total}</p>
//                     </div>
//                   )}

//                   {analysisResult.test_results && (
//                     <div>
//                       <h4>Test Cases</h4>
//                       {analysisResult.test_results.map((test, i) => (
//                         <div key={i} style={styles.testCaseBox(test.passed)}>
//                           <p><strong>Input:</strong> {test.input}</p>
//                           <p><strong>Expected:</strong> {test.expected}</p>
//                           <p><strong>Actual:</strong> {test.actual}</p>
//                           {test.runtime_error && <pre style={{ color: "#f44336" }}>{test.runtime_error}</pre>}
//                           <p>Status: {test.passed ? "Passed ✅" : "Failed ❌"}</p>
//                         </div>
//                       ))}
//                     </div>
//                   )}

//                   {analysisResult.logical_errors && analysisResult.logical_errors.length > 0 && (
//                     <div>
//                       <h4>Logical Errors</h4>
//                       {analysisResult.logical_errors.map((err, i) => (
//                         <div key={i} style={styles.logicalErrorBox}>
//                           <p><strong>Error:</strong> {err.what}</p>
//                           <p><strong>Where:</strong> {err.where}</p>
//                           <p><strong>Why:</strong> {err.why}</p>
//                           <p><strong>Hint:</strong> {err.hint}</p>
//                           <p><strong>Confidence:</strong> {err.confidence}</p>
//                           {err.code_snippet && <pre>{err.code_snippet}</pre>}
//                         </div>
//                       ))}
//                     </div>
//                   )}
//                 </div>
//               )}
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// export default CompilerPage;


import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Syne:wght@400;500;600;700;800&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg-base: #0d0f14;
    --bg-surface: #13161d;
    --bg-elevated: #1a1e27;
    --bg-hover: #1f2433;
    --border: #252a38;
    --border-bright: #2e3548;
    --accent: #4f9eff;
    --accent-glow: rgba(79, 158, 255, 0.15);
    --green: #3dd68c;
    --green-bg: rgba(61, 214, 140, 0.08);
    --red: #ff5f6d;
    --red-bg: rgba(255, 95, 109, 0.08);
    --amber: #f5a623;
    --text-primary: #e2e8f8;
    --text-secondary: #7b8ab8;
    --text-muted: #3f4a6b;
    --font-mono: 'JetBrains Mono', monospace;
    --font-ui: 'Syne', sans-serif;
  }

  .compiler-root {
    display: flex; height: 100vh;
    font-family: var(--font-ui);
    background: var(--bg-base); color: var(--text-primary); overflow: hidden;
  }

  .left-pane {
    width: 340px; min-width: 280px;
    display: flex; flex-direction: column;
    border-right: 1px solid var(--border);
    background: var(--bg-surface); overflow: hidden;
  }

  .left-header { padding: 20px 24px 16px; border-bottom: 1px solid var(--border); }

  .question-badge {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: var(--font-mono); font-size: 10px; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--accent); background: var(--accent-glow);
    border: 1px solid rgba(79, 158, 255, 0.2);
    padding: 4px 10px; border-radius: 4px; margin-bottom: 14px;
  }
  .question-badge::before {
    content: ''; width: 6px; height: 6px; border-radius: 50%;
    background: var(--accent); animation: pulse 2s infinite;
  }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

  .question-title {
    font-size: 17px; font-weight: 700; line-height: 1.3;
    color: var(--text-primary); letter-spacing: -0.02em;
  }
  .left-body { flex: 1; overflow-y: auto; padding: 20px 24px; scrollbar-width: thin; scrollbar-color: var(--border-bright) transparent; }
  .question-description { font-size: 13.5px; font-weight: 400; line-height: 1.75; color: var(--text-secondary); }

  .difficulty-tag {
    display: inline-block; margin-top: 16px;
    font-family: var(--font-mono); font-size: 10px; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    padding: 3px 9px; border-radius: 3px;
    background: rgba(245, 166, 35, 0.1); color: var(--amber);
    border: 1px solid rgba(245, 166, 35, 0.25);
  }

  .skeleton-line {
    height: 12px; border-radius: 4px; margin-bottom: 10px;
    background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-hover) 50%, var(--bg-elevated) 75%);
    background-size: 200% 100%; animation: shimmer 1.5s infinite;
  }
  @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

  .right-pane { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: var(--bg-base); }

  .top-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 20px; height: 48px;
    border-bottom: 1px solid var(--border);
    background: var(--bg-surface); flex-shrink: 0;
  }

  .tabs { display: flex; height: 100%; gap: 2px; }

  .tab-btn {
    display: flex; align-items: center; gap: 7px;
    padding: 0 16px; height: 100%;
    background: none; border: none; border-bottom: 2px solid transparent;
    color: var(--text-muted);
    font-family: var(--font-ui); font-size: 12px; font-weight: 600;
    letter-spacing: 0.05em; text-transform: uppercase;
    cursor: pointer; transition: all 0.2s;
  }
  .tab-btn:hover { color: var(--text-secondary); }
  .tab-btn.active { color: var(--text-primary); border-bottom-color: var(--accent); }
  .tab-icon { width: 14px; height: 14px; }

  .lang-indicator {
    display: flex; align-items: center; gap: 8px;
    font-family: var(--font-mono); font-size: 11px; font-weight: 500;
    color: var(--text-secondary);
    padding: 5px 10px; background: var(--bg-elevated);
    border: 1px solid var(--border); border-radius: 4px;
  }
  .lang-dot { width: 8px; height: 8px; border-radius: 50%; background: #4b8bbe; }

  .editor-wrapper { flex: 1; position: relative; overflow: hidden; display: flex; flex-direction: column; }

  .line-numbers {
    position: absolute; left: 0; top: 0; bottom: 0; width: 48px;
    padding: 16px 0; background: var(--bg-surface);
    border-right: 1px solid var(--border);
    display: flex; flex-direction: column;
    pointer-events: none; overflow: hidden; z-index: 1;
  }
  .line-num {
    font-family: var(--font-mono); font-size: 13px; line-height: 22px;
    padding-right: 12px; color: var(--text-muted);
    text-align: right; user-select: none;
  }

  .code-textarea {
    flex: 1; padding: 16px 16px 16px 64px;
    font-family: var(--font-mono); font-size: 13.5px; line-height: 22px;
    background: var(--bg-base); color: #c9d8ff;
    border: none; outline: none; resize: none; width: 100%;
    scrollbar-width: thin; scrollbar-color: var(--border-bright) transparent;
    caret-color: var(--accent); letter-spacing: 0.02em;
  }
  .code-textarea::placeholder { color: var(--text-muted); font-style: italic; }

  .action-bar {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 20px;
    border-top: 1px solid var(--border);
    background: var(--bg-surface); flex-shrink: 0;
  }

  .btn {
    display: flex; align-items: center; gap: 8px;
    padding: 9px 20px; border: none; border-radius: 6px;
    font-family: var(--font-ui); font-size: 12.5px; font-weight: 700;
    letter-spacing: 0.05em; text-transform: uppercase;
    cursor: pointer; transition: all 0.2s;
  }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }

  .btn-run { background: var(--green); color: #0a1f14; }
  .btn-run:hover:not(:disabled) { background: #52e8a0; box-shadow: 0 0 20px rgba(61,214,140,0.3); transform: translateY(-1px); }

  .btn-analyze { background: transparent; color: var(--accent); border: 1px solid rgba(79,158,255,0.35); }
  .btn-analyze:hover:not(:disabled) { background: var(--accent-glow); border-color: var(--accent); box-shadow: 0 0 20px var(--accent-glow); transform: translateY(-1px); }

  .btn-icon { width: 14px; height: 14px; }
  .spinner { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-top-color: currentColor; border-radius: 50%; animation: spin 0.7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  .action-spacer { flex: 1; }
  .char-count { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); }

  .output-pane {
    flex: 1; overflow-y: auto; padding: 24px;
    scrollbar-width: thin; scrollbar-color: var(--border-bright) transparent;
    display: flex; flex-direction: column; gap: 20px;
  }

  .output-section-label {
    display: flex; align-items: center; gap: 10px;
    font-family: var(--font-mono); font-size: 10px; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--text-muted); margin-bottom: 10px;
  }
  .output-section-label::after { content: ''; flex: 1; height: 1px; background: var(--border); }

  .console-block { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
  .console-header { display: flex; align-items: center; gap: 8px; padding: 10px 16px; border-bottom: 1px solid var(--border); background: var(--bg-elevated); }
  .console-dot { width: 10px; height: 10px; border-radius: 50%; }
  .console-title { font-family: var(--font-mono); font-size: 11px; font-weight: 600; color: var(--text-secondary); letter-spacing: 0.08em; text-transform: uppercase; margin-left: 4px; }
  .console-pre { padding: 16px; font-family: var(--font-mono); font-size: 13px; line-height: 1.7; color: #a8c0ff; white-space: pre-wrap; word-break: break-word; min-height: 60px; }

  .summary-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  .summary-card { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px; display: flex; flex-direction: column; gap: 4px; }
  .summary-card-label { font-family: var(--font-mono); font-size: 10px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); }
  .summary-card-value { font-family: var(--font-ui); font-size: 26px; font-weight: 800; letter-spacing: -0.03em; line-height: 1; }
  .value-green { color: var(--green); }
  .value-accent { color: var(--accent); }

  .test-grid { display: flex; flex-direction: column; gap: 8px; }
  .test-card { border-radius: 8px; border: 1px solid; overflow: hidden; }
  .test-card.passed { border-color: rgba(61,214,140,0.25); background: var(--green-bg); }
  .test-card.failed { border-color: rgba(255,95,109,0.25); background: var(--red-bg); }
  .test-card-header { display: flex; align-items: center; gap: 10px; padding: 10px 14px; }
  .test-status-badge { font-family: var(--font-mono); font-size: 10px; font-weight: 700; letter-spacing: 0.08em; padding: 2px 8px; border-radius: 3px; }
  .badge-pass { background: rgba(61,214,140,0.2); color: var(--green); }
  .badge-fail { background: rgba(255,95,109,0.2); color: var(--red); }
  .test-card-title { font-family: var(--font-mono); font-size: 12px; font-weight: 600; color: var(--text-secondary); }
  .test-card-body { padding: 0 14px 14px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
  .test-field-label { font-family: var(--font-mono); font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 4px; }
  .test-field-value { font-family: var(--font-mono); font-size: 12.5px; color: var(--text-secondary); background: rgba(0,0,0,0.25); padding: 6px 10px; border-radius: 4px; border: 1px solid var(--border); word-break: break-all; }
  .runtime-error-block { margin: 0 14px 14px; padding: 10px; background: rgba(255,95,109,0.08); border: 1px solid rgba(255,95,109,0.2); border-radius: 4px; font-family: var(--font-mono); font-size: 11.5px; color: var(--red); white-space: pre-wrap; }

  .error-list { display: flex; flex-direction: column; gap: 10px; }
  .error-card { background: rgba(255,95,109,0.05); border: 1px solid rgba(255,95,109,0.2); border-radius: 8px; overflow: hidden; }
  .error-card-header { display: flex; align-items: center; gap: 10px; padding: 12px 16px; border-bottom: 1px solid rgba(255,95,109,0.1); background: rgba(255,95,109,0.07); }
  .error-what { font-size: 13.5px; font-weight: 600; color: var(--text-primary); flex: 1; }
  .confidence-badge { font-family: var(--font-mono); font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 3px; background: rgba(245,166,35,0.15); color: var(--amber); border: 1px solid rgba(245,166,35,0.2); }
  .error-card-body { padding: 14px 16px; display: flex; flex-direction: column; gap: 10px; }
  .error-row { display: flex; gap: 10px; align-items: flex-start; }
  .error-row-label { font-family: var(--font-mono); font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); padding-top: 1px; min-width: 48px; }
  .error-row-text { font-size: 13px; line-height: 1.6; color: var(--text-secondary); flex: 1; }
  .hint-text { color: #a8c4ff; font-style: italic; }
  .error-snippet { background: var(--bg-base); border: 1px solid var(--border); border-radius: 6px; padding: 12px 14px; font-family: var(--font-mono); font-size: 12.5px; color: #c9d8ff; white-space: pre-wrap; line-height: 1.65; }

  .no-output-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; color: var(--text-muted); min-height: 300px; }
  .no-output-icon { font-size: 40px; opacity: 0.3; }
  .no-output-text { font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.05em; text-transform: uppercase; opacity: 0.5; }
`;

function CompilerPage() {
  const { questionId } = useParams();
  const [question, setQuestion] = useState(null);
  const [code, setCode] = useState("");
  const [runtimeOutput, setRuntimeOutput] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("code");

  const lineCount = code.split("\n").length;

  useEffect(() => {
    const fetchQuestion = async () => {
      try {
        const response = await fetch(`http://localhost:8080/api/questions/${questionId}`);
        const data = await response.json();
        setQuestion(data);
      } catch (err) { console.error("Error fetching question:", err); }
    };
    fetchQuestion();
  }, [questionId]);

  const handleRun = async () => {
    setLoading(true); setRuntimeOutput(""); setAnalysisResult(null);
    try {
      const response = await fetch(`http://localhost:8080/api/submissions/run/${questionId}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ studentId: 1, language: "python", code }),
      });
      const data = await response.json();
      if (data.length > 0) {
        const first = data[0];
        setRuntimeOutput(first.actualOutput || first.runtime_error || "No output");
        setActiveTab("output");
      }
    } catch (err) { setRuntimeOutput("Error running code."); setActiveTab("output"); }
    setLoading(false);
  };

  const handleAnalyze = async () => {
    setLoading(true); setAnalysisResult(null);
    try {
      const response = await fetch("http://localhost:8080/api/submissions/analyze", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ studentId: 1, questionId, language: "python", code }),
      });
      const data = await response.json();
      setAnalysisResult(data); setActiveTab("output");
    } catch (err) { console.error("Analyze error:", err); }
    setLoading(false);
  };

  const hasOutput = runtimeOutput || analysisResult;

  return (
    <>
      <style>{styles}</style>
      <div className="compiler-root">

        {/* LEFT PANE */}
        <div className="left-pane">
          <div className="left-header">
            <div className="question-badge">Problem #{questionId}</div>
            {question ? (
              <>
                <h2 className="question-title">{question.title}</h2>
                <span className="difficulty-tag">Medium</span>
              </>
            ) : (
              <div style={{ marginTop: 8 }}>
                <div className="skeleton-line" style={{ width: "60%" }} />
                <div className="skeleton-line" style={{ width: "80%" }} />
              </div>
            )}
          </div>
          <div className="left-body">
            {question ? (
              <p className="question-description">{question.description}</p>
            ) : (
              [100, 90, 95, 70, 85, 60].map((w, i) => (
                <div key={i} className="skeleton-line" style={{ width: `${w}%` }} />
              ))
            )}
          </div>
        </div>

        {/* RIGHT PANE */}
        <div className="right-pane">
          <div className="top-bar">
            <div className="tabs">
              <button className={`tab-btn ${activeTab === "code" ? "active" : ""}`} onClick={() => setActiveTab("code")}>
                <svg className="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" />
                </svg>
                Editor
              </button>
              <button className={`tab-btn ${activeTab === "output" ? "active" : ""}`} onClick={() => setActiveTab("output")}>
                <svg className="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="3" width="20" height="14" rx="2" />
                  <line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" />
                </svg>
                Output
              </button>
            </div>
            <div className="lang-indicator">
              <div className="lang-dot" /> Python 3
            </div>
          </div>

          {activeTab === "code" && (
            <>
              <div className="editor-wrapper">
                <div className="line-numbers">
                  {Array.from({ length: Math.max(lineCount, 20) }, (_, i) => (
                    <div key={i} className="line-num">{i + 1}</div>
                  ))}
                </div>
                <textarea
                  className="code-textarea"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="# Write your Python solution here..."
                  spellCheck={false}
                />
              </div>
              <div className="action-bar">
                <button className="btn btn-run" onClick={handleRun} disabled={loading}>
                  {loading ? <span className="spinner" /> : (
                    <svg className="btn-icon" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3" /></svg>
                  )}
                  {loading ? "Running..." : "Run Code"}
                </button>
                <button className="btn btn-analyze" onClick={handleAnalyze} disabled={loading}>
                  {loading ? <span className="spinner" /> : (
                    <svg className="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                    </svg>
                  )}
                  {loading ? "Analyzing..." : "Analyze"}
                </button>
                <div className="action-spacer" />
                <span className="char-count">{code.length} chars · {lineCount} lines</span>
              </div>
            </>
          )}

          {activeTab === "output" && (
            <div className="output-pane">
              {!hasOutput ? (
                <div className="no-output-state">
                  <div className="no-output-icon">⬡</div>
                  <p className="no-output-text">Run or analyze your code to see results</p>
                </div>
              ) : (
                <>
                  {runtimeOutput && (
                    <div>
                      <div className="output-section-label">Console</div>
                      <div className="console-block">
                        <div className="console-header">
                          <div className="console-dot" style={{ background: "#ff5f6d" }} />
                          <div className="console-dot" style={{ background: "#f5a623" }} />
                          <div className="console-dot" style={{ background: "#3dd68c" }} />
                          <span className="console-title">stdout</span>
                        </div>
                        <pre className="console-pre">{runtimeOutput}</pre>
                      </div>
                    </div>
                  )}

                  {analysisResult?.test_summary && (
                    <div>
                      <div className="output-section-label">Summary</div>
                      <div className="summary-row">
                        <div className="summary-card">
                          <span className="summary-card-label">Score</span>
                          <span className="summary-card-value value-accent">{analysisResult.test_summary.score}</span>
                        </div>
                        <div className="summary-card">
                          <span className="summary-card-label">Passed</span>
                          <span className="summary-card-value value-green">{analysisResult.test_summary.passed}</span>
                        </div>
                        <div className="summary-card">
                          <span className="summary-card-label">Total</span>
                          <span className="summary-card-value" style={{ color: "var(--text-secondary)" }}>{analysisResult.test_summary.total}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {analysisResult?.test_results && (
                    <div>
                      <div className="output-section-label">Test Cases</div>
                      <div className="test-grid">
                        {analysisResult.test_results.map((test, i) => (
                          <div key={i} className={`test-card ${test.passed ? "passed" : "failed"}`}>
                            <div className="test-card-header">
                              <span className={`test-status-badge ${test.passed ? "badge-pass" : "badge-fail"}`}>
                                {test.passed ? "PASS" : "FAIL"}
                              </span>
                              <span className="test-card-title">Test case #{i + 1}</span>
                            </div>
                            <div className="test-card-body">
                              <div><div className="test-field-label">Input</div><div className="test-field-value">{test.input}</div></div>
                              <div><div className="test-field-label">Expected</div><div className="test-field-value">{test.expected}</div></div>
                              <div><div className="test-field-label">Actual</div><div className="test-field-value">{test.actual}</div></div>
                            </div>
                            {test.runtime_error && <pre className="runtime-error-block">{test.runtime_error}</pre>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysisResult?.logical_errors?.length > 0 && (
                    <div>
                      <div className="output-section-label">Logical Errors</div>
                      <div className="error-list">
                        {analysisResult.logical_errors.map((err, i) => (
                          <div key={i} className="error-card">
                            <div className="error-card-header">
                              <span style={{ fontSize: 14 }}>⚠</span>
                              <span className="error-what">{err.what}</span>
                              {err.confidence && <span className="confidence-badge">{err.confidence}</span>}
                            </div>
                            <div className="error-card-body">
                              {err.where && <div className="error-row"><span className="error-row-label">Where</span><span className="error-row-text">{err.where}</span></div>}
                              {err.why && <div className="error-row"><span className="error-row-label">Why</span><span className="error-row-text">{err.why}</span></div>}
                              {err.hint && <div className="error-row"><span className="error-row-label">Hint</span><span className="error-row-text hint-text">{err.hint}</span></div>}
                              {err.code_snippet && <pre className="error-snippet">{err.code_snippet}</pre>}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default CompilerPage;