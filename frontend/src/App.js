import { useState } from "react";
import { sendQuery } from "./api";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const handleSend = async () => {
    const userMsg = { role: "user", text: input };
    setMessages([...messages, userMsg]);

    const response = await sendQuery(input);

    setMessages(prev => [...prev, { role: "bot", text: response }]);
    setInput("");
  };

  return (
    <div>
      <h1>UPOU Admissions Helpdesk</h1>

      {messages.map((msg, i) => (
        <p key={i}><b>{msg.role}:</b> {msg.text}</p>
      ))}

      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}

export default App;