import React from "react";
import { motion } from "framer-motion";

const Dashboard = () => (
  <motion.div
    className="page dashboard"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >
    <h1>Dashboard</h1>
    <p>Here you will see your uploaded files, embeddings, and AI answers.</p>
  </motion.div>
);

export default Dashboard;
