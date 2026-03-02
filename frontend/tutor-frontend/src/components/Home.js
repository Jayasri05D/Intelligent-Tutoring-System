

// import React, { useEffect, useState } from "react";
// import { useNavigate } from "react-router-dom";

// function Home() {
//   const navigate = useNavigate();
//   const [concepts, setConcepts] = useState([]);

//   useEffect(() => {
//     fetch("http://localhost:8080/api/concepts")
//       .then((res) => res.json())
//       .then((data) => setConcepts(data))
//       .catch((err) => console.error("Error fetching concepts:", err));
//   }, []);

//   return (
//     <div style={{ padding: "40px" }}>
//       <h2>Select a Concept</h2>

//       {concepts.length === 0 ? (
//         <p>No concepts available</p>
//       ) : (
//         concepts.map((concept) => (
//           <div
//             key={concept.id}
//             onClick={() => navigate(`/concept/${concept.id}`)}
//             style={{
//               border: "1px solid black",
//               padding: "15px",
//               margin: "10px",
//               cursor: "pointer"
//             }}
//           >
//             {concept.name}
//           </div>
//         ))
//       )}
//     </div>
//   );
// }

// export default Home;


//code with css
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

  const styles = {
    container: {
      padding: "40px",
      fontFamily: "Arial, sans-serif",
      background: "#f4f4f4",
      minHeight: "100vh"
    },
    header: {
      marginBottom: "30px",
      color: "#333"
    },
    conceptCard: {
      border: "1px solid #ccc",
      borderRadius: "8px",
      padding: "20px",
      marginBottom: "15px",
      background: "#fff",
      cursor: "pointer",
      boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
      transition: "all 0.2s ease",
      fontSize: "16px",
      fontWeight: "bold",
      color: "#1a237e",
    },
    conceptCardHover: {
      transform: "translateY(-3px)",
      boxShadow: "0 4px 10px rgba(0,0,0,0.15)",
      borderColor: "#2196F3",
    },
    noConcepts: {
      color: "#777",
      fontStyle: "italic"
    }
  };

  const [hoveredId, setHoveredId] = useState(null);

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>Select a Concept</h2>

      {concepts.length === 0 ? (
        <p style={styles.noConcepts}>No concepts available</p>
      ) : (
        concepts.map((concept) => (
          <div
            key={concept.id}
            onClick={() => navigate(`/concept/${concept.id}`)}
            style={{
              ...styles.conceptCard,
              ...(hoveredId === concept.id ? styles.conceptCardHover : {})
            }}
            onMouseEnter={() => setHoveredId(concept.id)}
            onMouseLeave={() => setHoveredId(null)}
          >
            {concept.name}
          </div>
        ))
      )}
    </div>
  );
}

export default Home;


