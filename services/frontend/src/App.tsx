import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [list, setList] = useState<string[]>([]);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);

  useEffect(() => {
    fetchDataGet();
  }, []);

  const fetchDataGet = async () => {
    try {
      const response = await fetch("/api/solverhandler", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      setList(Object.values(data));
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleItemClick = (value: string) => {
    const newList = [...selectedItems];
    newList.push(value);
    setSelectedItems(newList);
  };

  const fetchPostSolvers = async () => {
    console.log(selectedItems);
    try {
      const response = await fetch("/api/startsolvers", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(selectedItems),
      });

      // Handle the response as needed
      console.log(response);
    } catch (error) {
      console.error("Error posting solvers:", error);
    }
  };

  return (
    <>
      <h1>List . Solvers</h1>
      <div>
        <ul>
          {list.map((value) => (
            <li key={value} style={{ display: "flex", alignItems: "center" }}>
              <input
                type="checkbox"
                checked={selectedItems.includes(value)}
                onChange={() => handleItemClick(value)}
              />
              <span>{value}</span>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <button onClick={() => fetchPostSolvers()}>Fetch POST</button>
      </div>
    </>
  );
}

export default App;
