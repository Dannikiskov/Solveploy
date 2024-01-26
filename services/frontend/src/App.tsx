import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [list, setList] = useState<{ [key: string]: string }>({});
  const [selectedItems, setSelectedItems] = useState<{ [key: string]: string }>(
    {}
  );

  useEffect(() => {
    fetchDataGet("/api/solverhandler");
  }, []);

  const fetchDataGet = async (endpoint: string) => {
    try {
      const response = await fetch(endpoint, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      setList(data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleItemClick = (key: string) => {
    setSelectedItems((prevSelectedItems) => ({
      ...prevSelectedItems,
      [key]: prevSelectedItems[key] ? "" : list[key],
    }));
  };

  return (
    <>
      <h1>Select Solvers</h1>
      <div>
        <ul>
          {Object.keys(list).map((key) => (
            <li key={key} style={{ display: "flex", alignItems: "center" }}>
              <input
                type="checkbox"
                checked={!!selectedItems[key]}
                onChange={() => handleItemClick(key)}
              />
              <span>{list[key]}</span>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <button onClick={() => console.log(selectedItems)}>
          Fetch Hello POST (Textbox 2)
        </button>
      </div>
    </>
  );
}

export default App;
