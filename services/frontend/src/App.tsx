import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [modelString, setModelString] = useState("");

  async function fetchData() {
    try {
      // Create a new JSON object containing the MiniZinc model string.
      const jsonData = {
        model_string: modelString,
      };

      // Send a POST request to the /api/solver endpoint with the JSON object as the body of the request.
      const response = await fetch("api/solver", {
        method: "POST",
        headers: new Headers({
          "Content-Type": "application/json",
        }),
        body: JSON.stringify(jsonData),
      });

      // Check if the response was successful.
      if (response.status === 200) {
        // Parse the JSON response to extract the results of the MiniZinc solve.
        const json = await response.json();

        // Update the state variables with the results of the MiniZinc solve.
        setMessage(json.message);
      } else {
        // Handle the error.
        console.error("Error fetching data:", response.statusText);
      }
    } catch (error) {
      // Handle the error.
      console.error("Error fetching data:", error);
    }
  }

  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank">
          {" "}
          q
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>

      <h1>Vite + React</h1>

      <div className="card">
        {/* Use a textarea instead of an input for multiline text */}
        <textarea
          value={modelString}
          onChange={(e) => setModelString(e.target.value)}
        />
        <button
          onClick={() => {
            fetchData();
          }}
        >
          Send Model
        </button>
        <p>{message}</p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  );
}

export default App;
