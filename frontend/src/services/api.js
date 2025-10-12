const API_URL = "http://localhost:8000";

export async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch(`${API_URL}/login/`, {
    method: "POST",
    body: formData,
    credentials: "include"
  });
  return res.json();
}

export async function query(question) {
  const res = await fetch(`${API_URL}/query/`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ question }),
    credentials: "include"
  });
  return res.text();
}