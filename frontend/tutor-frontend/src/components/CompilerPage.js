// import React, { useState } from "react";
// import { useParams } from "react-router-dom";

// function CompilerPage() {
//   const { questionId } = useParams();

//   const [code, setCode] = useState("");
//   const [runtimeOutput, setRuntimeOutput] = useState("");
//   const [analysisResult, setAnalysisResult] = useState(null);
//   const [loading, setLoading] = useState(false);

//   // 🔹 RUN CODE
//   const handleRun = async () => {
//   setLoading(true);
//   setRuntimeOutput("");
//   setAnalysisResult(null);

//   try {
//     const response = await fetch(
//       `http://localhost:8080/api/submissions/${questionId}`,
//       {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json"
//         },
//         body: JSON.stringify({
//           studentId: 1,
//           language: "python",
//           code: code
//         })
//       }
//     );

//     const data = await response.json();
//     console.log(data);

//     setRuntimeOutput(
//       data.runtimeError
//         ? data.runtimeError
//         : data.runtimeOutput || "Program executed successfully (no output)"
//     );

//   } catch (error) {
//     setRuntimeOutput("Error while running code.");
//   }

//   setLoading(false);
// };
//   // 🔹 ANALYZE CODE
//   const handleAnalyze = async () => {
//     setLoading(true);
//     setAnalysisResult(null);

//     try {
//       const response = await fetch("http://localhost:8080/api/submissions/analyze", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json"
//         },
//         body: JSON.stringify({
//           studentId: 1,
//           language: "python",
//           code: code
//         })
//       });

//       const data = await response.json();
//       setAnalysisResult(data);

//     } catch (error) {
//       console.error(error);
//     }

//     setLoading(false);
//   };

//   return (
//     <div style={{ display: "flex", height: "100vh" }}>
      
//       {/* LEFT SIDE – QUESTION */}
//       <div style={{ width: "40%", padding: "20px", borderRight: "1px solid gray" }}>
//         <h3>Question {questionId}</h3>
//         <p>
//           Write a function to reverse an array.
//         </p>
//       </div>

//       {/* RIGHT SIDE – COMPILER */}
//       <div style={{ width: "60%", padding: "20px" }}>
        
//         <textarea
//           rows="15"
//           cols="70"
//           value={code}
//           onChange={(e) => setCode(e.target.value)}
//         />

//         <br /><br />

//         <button onClick={handleRun} style={{ marginRight: "10px" }}>
//           {loading ? "Running..." : "Run Code"}
//         </button>

//         <button onClick={handleAnalyze}>
//           {loading ? "Analyzing..." : "Analyze Code"}
//         </button>

//         {/* 🔹 Console Output */}
//         {runtimeOutput && (
//           <div style={{
//             backgroundColor: "black",
//             color: "lime",
//             marginTop: "20px",
//             padding: "10px",
//             fontFamily: "monospace"
//           }}>
//             <h4 style={{ color: "white" }}>Console Output</h4>
//             <pre>{runtimeOutput}</pre>
//           </div>
//         )}

//         {/* 🔹 Analysis Result */}
//         {analysisResult && (
//           <div style={{ marginTop: "20px" }}>
//             <h4>Analysis Result</h4>

//             <p>
//               <strong>Syntax Error:</strong>{" "}
//               {analysisResult.has_syntax_error ? "Yes" : "No"}
//             </p>

//             {analysisResult.violations &&
//             analysisResult.violations.length > 0 ? (
//               analysisResult.violations.map((v, index) => (
//                 <div
//                   key={index}
//                   style={{
//                     border: "1px solid red",
//                     padding: "10px",
//                     margin: "10px 0"
//                   }}
//                 >
//                   <p><strong>Rule:</strong> {v.rule_id}</p>
//                   <p><strong>Concept:</strong> {v.concept}</p>
//                   <p><strong>Line:</strong> {v.line}</p>
//                   <p><strong>Confidence:</strong> {v.confidence}</p>
//                   <p><strong>Violation:</strong> {v.violated_principle}</p>
//                   <p><strong>Explanation:</strong> {v.explanation}</p>
//                   <p><strong>Why It Matters:</strong> {v.why_it_matters}</p>
//                 </div>
//               ))
//             ) : (
//               <p>No violations detected 🎉</p>
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

  // 🔹 FETCH QUESTION FROM BACKEND
  useEffect(() => {
    const fetchQuestion = async () => {
      try {
        const response = await fetch(
          `http://localhost:8080/api/questions/${questionId}`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch question");
        }

        const data = await response.json();
        console.log("Fetched Question:", data);
        setQuestion(data);

      } catch (error) {
        console.error("Error fetching question:", error);
      }
    };

    fetchQuestion();
  }, [questionId]);

  // 🔹 RUN CODE
  const handleRun = async () => {
    setLoading(true);
    setRuntimeOutput("");
    setAnalysisResult(null);

    try {
      const response = await fetch(
        `http://localhost:8080/api/submissions/${questionId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            studentId: 1,
            language: "python",
            code: code
          })
        }
      );

      const data = await response.json();
      console.log("Run Response:", data);

      setRuntimeOutput(
  data.runtime_error
    ? data.runtime_error
    : data.runtime_output || "Program executed successfully (no output)"
);

    } catch (error) {
      setRuntimeOutput("Error while running code.");
    }

    setLoading(false);
  };

  // 🔹 ANALYZE CODE
  const handleAnalyze = async () => {
    setLoading(true);
    setAnalysisResult(null);

    try {
      const response = await fetch(
        "http://localhost:8080/api/submissions/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            studentId: 1,
            language: "python",
            code: code
          })
        }
      );

      const data = await response.json();
      console.log("Analysis Response:", data);
      setAnalysisResult(data);

    } catch (error) {
      console.error("Error analyzing code:", error);
    }

    setLoading(false);
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      
      {/* 🔹 LEFT SIDE – QUESTION */}
      <div style={{ width: "40%", padding: "20px", borderRight: "1px solid gray" }}>
        <h3>Question {questionId}</h3>

        {question ? (
          <>
            <h4>{question.title}</h4>
            <p>{question.description}</p>

            {question.difficulty && (
              <p><strong>Difficulty:</strong> {question.difficulty}</p>
            )}

            {question.sampleInput && (
              <>
                <h5>Sample Input:</h5>
                <pre>{question.sampleInput}</pre>
              </>
            )}

            {question.sampleOutput && (
              <>
                <h5>Sample Output:</h5>
                <pre>{question.sampleOutput}</pre>
              </>
            )}
          </>
        ) : (
          <p>Loading question...</p>
        )}
      </div>

      {/* 🔹 RIGHT SIDE – COMPILER */}
      <div style={{ width: "60%", padding: "20px" }}>
        
        <textarea
          rows="15"
          cols="70"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Write your Python code here..."
        />

        <br /><br />

        <button onClick={handleRun} style={{ marginRight: "10px" }}>
          {loading ? "Processing..." : "Run Code"}
        </button>

        <button onClick={handleAnalyze}>
          {loading ? "Processing..." : "Analyze Code"}
        </button>

        {/* 🔹 Console Output */}
        {runtimeOutput && (
          <div
            style={{
              backgroundColor: "black",
              color: "lime",
              marginTop: "20px",
              padding: "10px",
              fontFamily: "monospace"
            }}
          >
            <h4 style={{ color: "white" }}>Console Output</h4>
            <pre>{runtimeOutput}</pre>
          </div>
        )}

        {/* 🔹 Analysis Result */}
        {analysisResult && (
          <div style={{ marginTop: "20px" }}>
            <h4>Analysis Result</h4>

            <p>
              <strong>Syntax Error:</strong>{" "}
              {analysisResult.has_syntax_error ? "Yes" : "No"}
            </p>

            {analysisResult.violations &&
            analysisResult.violations.length > 0 ? (
              analysisResult.violations.map((v, index) => (
                <div
                  key={index}
                  style={{
                    border: "1px solid red",
                    padding: "10px",
                    margin: "10px 0"
                  }}
                >
                  <p><strong>Rule:</strong> {v.rule_id}</p>
                  <p><strong>Concept:</strong> {v.concept}</p>
                  <p><strong>Line:</strong> {v.line}</p>
                  <p><strong>Confidence:</strong> {v.confidence}</p>
                  <p><strong>Violation:</strong> {v.violated_principle}</p>
                  <p><strong>Explanation:</strong> {v.explanation}</p>
                  <p><strong>Why It Matters:</strong> {v.why_it_matters}</p>
                </div>
              ))
            ) : (
              <p>No violations detected 🎉</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default CompilerPage;