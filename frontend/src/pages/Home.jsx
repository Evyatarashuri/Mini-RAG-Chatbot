import React from "react";
import { motion } from "framer-motion";

const Home = () => (
  <motion.div
    className="page home"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >
    <h1>Welcome to RAG Chatbot</h1>
    <p>
      Upload your PDFs, ask smart questions, and get context-aware answers powered by AI.
    </p>
  </motion.div>
);

export default Home;
