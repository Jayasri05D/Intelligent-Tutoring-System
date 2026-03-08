

// import React, { useEffect, useState } from "react";
// import { useParams, useNavigate } from "react-router-dom";

// function ConceptPage() {
//   const { conceptId } = useParams();
//   const navigate = useNavigate();
//   const [questions, setQuestions] = useState([]);

//   useEffect(() => {
//     fetch(`http://localhost:8080/api/questions/concept/${conceptId}`)
//       .then((res) => res.json())
//       .then((data) => setQuestions(data))
//       .catch((err) => console.error("Error fetching questions:", err));
//   }, [conceptId]);

//   return (
//     <div style={{ padding: "40px" }}>
//       <h2>Questions</h2>

//       {questions.length === 0 ? (
//         <p>No questions available</p>
//       ) : (
//         questions.map((q) => (
//           <div
//             key={q.id}
//             onClick={() => navigate(`/solve/${q.id}`)}
//             style={{
//               border: "1px solid blue",
//               padding: "10px",
//               margin: "10px",
//               cursor: "pointer"
//             }}
//           >
//             <h4>{q.title}</h4>
//             <p>Difficulty: {q.difficulty}</p>
//           </div>
//         ))
//       )}
//     </div>
//   );
// }

// export default ConceptPage;

import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

function ConceptPage() {
  const { conceptId } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    fetch(`http://localhost:8080/api/questions/concept/${conceptId}`)
      .then((res) => res.json())
      .then((data) => setQuestions(data))
      .catch((err) => console.error("Error fetching questions:", err));
  }, [conceptId]);

  const styles = {
    container: { padding: "40px", fontFamily: "Arial, sans-serif", background: "#f4f4f4", minHeight: "100vh" },
    header: { marginBottom: "30px", color: "#333" },
    questionCard: {
      border: "1px solid #ccc",
      borderRadius: "8px",
      padding: "20px",
      marginBottom: "15px",
      background: "#fff",
      cursor: "pointer",
      boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
      transition: "all 0.2s ease",
    },
    questionCardHover: {
      transform: "translateY(-3px)",
      boxShadow: "0 4px 10px rgba(0,0,0,0.15)",
      borderColor: "#2196F3",
    },
    title: { margin: 0, marginBottom: "8px", color: "#1a237e" },
    difficulty: { color: "#555", fontSize: "14px" },
    noQuestions: { color: "#777", fontStyle: "italic" }
  };

  // To handle hover effect
  const [hoveredId, setHoveredId] = useState(null);

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>Questions for Concept {conceptId}</h2>

      {questions.length === 0 ? (
        <p style={styles.noQuestions}>No questions available</p>
      ) : (
        questions.map((q) => (
          <div
            key={q.id}
            onClick={() => navigate(`/solve/${q.id}`)}
            style={{
              ...styles.questionCard,
              ...(hoveredId === q.id ? styles.questionCardHover : {})
            }}
            onMouseEnter={() => setHoveredId(q.id)}
            onMouseLeave={() => setHoveredId(null)}
          >
            <h4 style={styles.title}>{q.title}</h4>
            <p style={styles.difficulty}>Difficulty: {q.difficulty}</p>
          </div>
        ))
      )}
    </div>
  );
}

export default ConceptPage;