import { useState } from "react";
import "./App.css";

function App() {
  const [message1, setMessage1] = useState<string>("");
  const [message2, setMessage2] = useState<string>("");

  const fetchData = async (
    endpoint: string,
    method: string,
    setMessage: Function
  ) => {
    try {
      const response = await fetch(`${endpoint}`, {
        method: `${method}`,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: setMessage === setMessage1 ? message1 : message2,
        }),
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
      <div>
        <textarea
          value={message1}
          onChange={(e) => setMessage1(e.target.value)}
        />
        <br></br>
        <button
          onClick={() => fetchData(`/api/solverjob`, "POST", setMessage1)}
        >
          Fetch Hello POST (Textbox 1)
        </button>
      </div>
      <br></br>
      <br></br>
      <div>
        <textarea
          value={message2}
          onChange={(e) => setMessage2(e.target.value)}
        />
        <br></br>
        <button
          onClick={() => fetchData(`/api/solver-database`, "POST", setMessage2)}
        >
          Fetch Another POST (Textbox 2)
        </button>
      </div>
    </>
  );
}

export default App;
