// import React from "react";
// import CodeAnalyzer from "./components/CodeAnalyzer";

// function App() {
//   return <CodeAnalyzer />;
// }

// export default App;

import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Home from "./components/Home";
import ConceptPage from "./components/ConceptPage";

import CompilerPage from "./components/CompilerPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/concept/:conceptId" element={<ConceptPage />} />
       
        <Route path="/solve/:questionId" element={<CompilerPage />} />
        <Route path="/solve/:questionId" element={<CompilerPage />} />
      </Routes>
    </Router>
  );
}

export default App;