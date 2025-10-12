import React from "react";
import { Link, useLocation } from "react-router-dom";

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="navbar">
      <h2 className="logo">Mini RAG Chatbot</h2>
      <div className="nav-links">
        <Link className={location.pathname === "/" ? "active" : ""} to="/">Home</Link>
        <Link className={location.pathname === "/login" ? "active" : ""} to="/login">Login</Link>
        <Link className={location.pathname === "/dashboard" ? "active" : ""} to="/dashboard">Dashboard</Link>
      </div>
    </nav>
  );
};

export default Navbar;
