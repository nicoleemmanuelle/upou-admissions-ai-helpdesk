export async function sendQuery(query) {
  const res = await fetch(import.meta.env.VITE_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    throw new Error("API request failed");
  }

  const data = await res.json();
  return data.response;
}
