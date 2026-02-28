// import React from "react";
// import { useParams, useNavigate } from "react-router-dom";

// function ConceptPage() {
//   const { conceptName } = useParams();
//   const navigate = useNavigate();

//   // Dummy questions (later fetch from backend)
//   const questions = [
//     { id: 1, title: "Find Maximum Element" },
//     { id: 2, title: "Reverse Array" },
//     { id: 3, title: "Sum of Elements" }
//   ];

//   return (
//     <div style={{ padding: "40px" }}>
//       <h2>{conceptName} Questions</h2>

//       {questions.map((q) => (
//         <div
//           key={q.id}
//           onClick={() => navigate(`/solve/${q.id}`)}
//           style={{
//             border: "1px solid blue",
//             padding: "10px",
//             margin: "10px",
//             cursor: "pointer"
//           }}
//         >
//           {q.title}
//         </div>
//       ))}
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

  return (
    <div style={{ padding: "40px" }}>
      <h2>Questions</h2>

      {questions.length === 0 ? (
        <p>No questions available</p>
      ) : (
        questions.map((q) => (
          <div
            key={q.id}
            onClick={() => navigate(`/solve/${q.id}`)}
            style={{
              border: "1px solid blue",
              padding: "10px",
              margin: "10px",
              cursor: "pointer"
            }}
          >
            <h4>{q.title}</h4>
            <p>Difficulty: {q.difficulty}</p>
          </div>
        ))
      )}
    </div>
  );
}

export default ConceptPage;