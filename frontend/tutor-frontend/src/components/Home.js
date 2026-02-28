// import React from "react";
// import { useNavigate } from "react-router-dom";

// function Home() {
//   const navigate = useNavigate();

//   const concepts = ["Arrays", "Strings", "Loops", "Recursion"];

//   return (
//     <div style={{ padding: "40px" }}>
//       <h2>Select a Concept</h2>

//       {concepts.map((concept, index) => (
//         <div
//           key={index}
//           onClick={() => navigate(`/concept/${concept}`)}
//           style={{
//             border: "1px solid black",
//             padding: "15px",
//             margin: "10px",
//             cursor: "pointer"
//           }}
//         >
//           {concept}
//         </div>
//       ))}
//     </div>
//   );
// }

// export default Home;

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();
  const [concepts, setConcepts] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8080/api/concepts")
      .then((res) => res.json())
      .then((data) => setConcepts(data))
      .catch((err) => console.error("Error fetching concepts:", err));
  }, []);

  return (
    <div style={{ padding: "40px" }}>
      <h2>Select a Concept</h2>

      {concepts.length === 0 ? (
        <p>No concepts available</p>
      ) : (
        concepts.map((concept) => (
          <div
            key={concept.id}
            onClick={() => navigate(`/concept/${concept.id}`)}
            style={{
              border: "1px solid black",
              padding: "15px",
              margin: "10px",
              cursor: "pointer"
            }}
          >
            {concept.name}
          </div>
        ))
      )}
    </div>
  );
}

export default Home;