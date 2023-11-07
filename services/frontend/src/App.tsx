import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";

function App() {
  //var backend = "http://my-backend-service.default.svc.cluster.local:5000/api/hello";
  const [count, setCount] = useState(0);
  const [message, setMessage] = useState("");

  async function fetchData() {
    try {
      const response = await fetch("/api/hello"); // Relative URL
      const json = await response.json();
      setMessage(json.message);
    } catch (error) {
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
        <button
          onClick={() => {
            setCount((count) => count + 1);
            fetchData();
          }}
        >
          count is {count}
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
