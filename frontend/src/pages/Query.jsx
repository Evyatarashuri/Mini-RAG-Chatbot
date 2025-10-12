import { useState } from "react";

function Query() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();
    setError("");
    setAnswer("");
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("question", question);

      const response = await fetch("http://localhost:8000/api/query/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
        credentials: "include",
      });

      const data = await response.json();
      setAnswer(data);
    } catch (err) {
      setError("Something went wrong while fetching the answer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2>Ask about your document</h2>
      <form onSubmit={handleAsk} style={styles.form}>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question..."
          style={styles.textarea}
        />
        <button type="submit" disabled={loading} style={styles.button}>
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>

      {error && <p style={styles.error}>{error}</p>}

      {answer && (
        <div style={styles.answerBox}>
          <h3>Answer:</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: "600px",
    margin: "0 auto",
    padding: "2rem",
    textAlign: "center",
    fontFamily: "sans-serif",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
  },
  textarea: {
    minHeight: "100px",
    padding: "10px",
    fontSize: "16px",
    borderRadius: "8px",
    border: "1px solid #ccc",
  },
  button: {
    backgroundColor: "#007bff",
    color: "white",
    padding: "10px",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },
  error: {
    color: "red",
    fontSize: "14px",
  },
  answerBox: {
    background: "#f8f9fa",
    padding: "1rem",
    borderRadius: "8px",
    marginTop: "1rem",
    textAlign: "left",
  },
};

export default Query;
