const API_URL = "https://qzt2pk1lue.execute-api.us-east-1.amazonaws.com/dev/ask";

export async function sendQuery(query) {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  const data = await res.json();
  if (data.error) throw new Error(data.error);
  return data.response;
}