import React, { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setIsUploading(true);
      setMessage("");

      const res = await fetch(`${API_URL}/api/documents/`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });

      const data = await res.json();

      if (res.ok) {
        setMessage(`✅ File "${data.filename}" uploaded successfully!`);
      } else {
        setMessage(`❌ Upload failed: ${data.error || res.statusText}`);
      }
    } catch (err) {
      setMessage("❌ Network error, please try again later.");
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white shadow-md rounded-xl p-8 w-full max-w-md">
        <h1 className="text-2xl font-semibold mb-6 text-center text-gray-800">
          Upload a PDF Document
        </h1>
        <form onSubmit={handleUpload} className="flex flex-col gap-4">
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0])}
            className="border rounded-lg px-4 py-2"
          />
          <button
            type="submit"
            disabled={isUploading}
            className={`${
              isUploading ? "bg-gray-400" : "bg-blue-500 hover:bg-blue-600"
            } text-white py-2 px-4 rounded-lg transition`}
          >
            {isUploading ? "Uploading..." : "Upload"}
          </button>
        </form>
        {message && (
          <p
            className={`mt-4 text-center ${
              message.startsWith("✅")
                ? "text-green-600"
                : message.startsWith("❌")
                ? "text-red-500"
                : "text-gray-700"
            }`}
          >
            {message}
          </p>
        )}
      </div>
    </div>
  );
}
