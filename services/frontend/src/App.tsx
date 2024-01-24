import { useState } from "react";
import "./App.css";

function App() {
  const [message1, setMessage1] = useState<string>("");

  const fetchDataPost = async (endpoint: string, setMessage: Function) => {
    try {
      const response = await fetch(`${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: message1,
        }),
      });

      const text = await response.text();
      setMessage(text);
    } catch (error) {
      console.error("Error fetching data:", error);
      setMessage(`Error fetching data, ${error}`);
    }
  };

  const fetchDataGet = async (endpoint: string, setMessage: Function) => {
    try {
      const response = await fetch(`${endpoint}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const text = await response.text();
      setMessage(text);
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
          onClick={() => fetchDataPost(`/api/solverhandler`, setMessage1)}
        >
          change?(Textbox 1)
        </button>
      </div>
      <div>
        <button onClick={() => fetchDataGet(`/api/solverhandler`, setMessage1)}>
          Fetch Hello POST (Textbox 2)
        </button>
      </div>
    </>
  );
}

export default App;
