export async function sendQuery(query) {
  const res = await fetch("YOUR_API_GATEWAY_URL", {
    method: "POST",
    body: JSON.stringify({ query }),
  });

  const data = await res.json();
  return data.response;
}