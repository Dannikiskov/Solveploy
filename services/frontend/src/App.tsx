import { useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState<string>("");

  const fetchData = async (endpoint: string, method: string) => {
    try {
      const response = await fetch(`${endpoint}`, {
        method: `${method}`,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      const text = await response.text();
      setMessage(text.slice(1, -2));
    } catch (error) {
      console.error("Error fetching data:", error);
      setMessage(`Error fetching data, ${error}`);
    }
  };

  return (
    <>
      <h1>Endpoint test</h1>
      <textarea value={message} onChange={(e) => setMessage(e.target.value)} />
      <br />
      <button onClick={() => fetchData(`/api/solverjob`, "POST")}>
        Fetch Hello GET
      </button>
    </>
  );
}

export default App;
