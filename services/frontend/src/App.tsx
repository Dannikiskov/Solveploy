import { useState, useEffect } from "react";
import "./App.css";

interface SolverData {
  name: string;
  id: string;
}

interface SolverResult {
  solverName: string;
  result: string;
  executionTime: number;
}

function App() {
  const [list, setList] = useState<SolverData[]>([]);
  const [selectedItems, setSelectedItems] = useState<SolverData[]>([]);
  const [mznFileContent, setMznFileContent] = useState<string>("");
  const [solverResultsList, setSolverResultsList] = useState<SolverResult[]>(
    []
  );

  useEffect(() => {
    fetchDataGet();
  }, []);

  const fetchDataGet = async () => {
    try {
      const response = await fetch("/api/solvers", {
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

  const handleItemClick = (item: SolverData) => {
    if (selectedItems.find((i) => i.name === item.name)) {
      setSelectedItems((prevItems) =>
        prevItems.filter((i) => i.name !== item.name)
      );
    } else {
      setSelectedItems((prevItems) => [...prevItems, item]);
    }
  };

  const handleStartSolvers = async () => {
    try {
      selectedItems.forEach(async (item, index) => {
        setSolverResultsList((prevResults) => [
          ...prevResults,
          {
            solverName: item.name,
            result: "",
            executionTime: 0,
          },
        ]);

        try {
          const response = await fetch("/api/startsolver", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              selectedItem: item,
              mznFileContent,
            }),
          });

          if (!response.ok) {
            throw new Error(
              `Error starting solver ${item.name}: ${response.statusText}`
            );
          }

          const resultData = await response.json();

          setSolverResultsList((prevResults) => {
            const updatedResults = [...prevResults];
            updatedResults[index] = {
              solverName: item.name,
              result: resultData.result,
              executionTime: resultData.executionTime,
            };
            return updatedResults;
          });
        } catch (error) {
          console.error(`Error starting solver ${item.name}:`, error);
        }
      });
    } catch (error) {
      console.error("Error starting solvers:", error);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result;
        console.log(content);
        console.log(mznFileContent);
        setMznFileContent(reader.result as string);
      };
      reader.readAsText(file);
    }
  };

  return (
    <>
      <h1>Solveploy</h1>
      <div>
        Upload .mzn: <br></br>
        <input onChange={handleFileChange} type="file" />
      </div>
      <br></br>
      <h2>Available Solvers</h2>
      <div className="grid">
        {list.map((item, index) => (
          <div
            key={index}
            className={`solver-item ${
              selectedItems.includes(item) ? "selected" : ""
            }`}
            onClick={() => handleItemClick(item)}
          >
            <div>Name: {item.name}</div>
            <div>ID: {item.id}</div>
          </div>
        ))}
      </div>
      <br></br>
      <button onClick={handleStartSolvers}>Start Solvers</button>
      <br></br>
      <div>
        <h2>Solver Results</h2>
        <div className="grid">
          {solverResultsList.map((item, index) => (
            <div key={index} className="solver-item">
              {item.result === "" ? (
                <>
                  <div>Name: {item.solverName}</div>
                  <div>Waiting for results...</div>
                </>
              ) : (
                <>
                  <div>Name: {item.solverName}</div>
                  <div>Result: {item.result}</div>
                  <div>Execution Time: {item.executionTime}</div>
                </>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default App;
