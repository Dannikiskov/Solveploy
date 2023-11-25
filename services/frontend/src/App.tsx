import { useState } from "react";
import "./App.css";

/*interface ApiResponse {
  message: string;
  data?: any;
}*/

function App() {
  const [message, setMessage] = useState<string>("");

  const fetchData = async (endpoint: string, method: string) => {
    try {
      const response = await fetch(`${endpoint}`, {
        method: `${method}`,
        headers: {
          "Content-Type": "application/json",
        },
      });
      console.log("JUST BEFORE APIreSPONEcast");
      //const data: ApiResponse = await response.text();
      const text = await response.text();
      console.log("JUST BEFORE JSONSTRINGIFY");
      setMessage(text);
      console.log("JUST AFTER JSONSTRINGIFY");
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
      <button onClick={() => fetchData("/api/hello", "GET")}>
        Fetch Hello GET
      </button>
    </>
  );
}

export default App;
