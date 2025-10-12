import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Query from "./pages/Query.jsx";
import Upload from "./pages/Upload.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/query" element={<Query />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </Router>
  </React.StrictMode>
);
