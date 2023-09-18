import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch("http://localhost:3001/api/todos");
      const todos = await response.json();
      setData(todos);
    };
    fetchData();
  }, []);

  return (
    <div>
      {data?.todos.map((stuff) => (
        <p key={stuff.key}>{stuff.text}</p>
      ))}
    </div>
  );
}

export default App;
