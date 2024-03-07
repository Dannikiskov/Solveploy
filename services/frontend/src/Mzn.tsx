import { useState } from "react";
import { useEffect } from "react";
import { v4 as uuidv4 } from "uuid";

import "./App.css";

interface MznSolverData {
  name: string;
  mznIdentifier: string;
  solverIdentifier: string;
}

interface MznJobResult extends MznSolverData {
  result: string;
  executionTime: number;
}

function Mzn() {
  const [mznSolverList, setMznSolverList] = useState<MznSolverData[]>([]);
  const [selectedMznSolvers, setSelectedMznSolvers] = useState<MznSolverData[]>([]);
  const [mznFileContent, setMznFileContent] = useState<string>("");
  const [runningMznJobs, setRunningMznJobs] = useState<MznSolverData[]>([]);
  const [mznJobResultList, setMznJobResultList] = useState<MznJobResult[]>([]);

  useEffect(() => {
    fetchDataGet();
  }, []);

  const fetchStopJob = async (item: MznSolverData) => {
    setRunningMznJobs((prevItems : Array<MznSolverData>) =>
      prevItems.filter((i) => i.name !== item.name)
    );

    try {
      const response = await fetch("/api/jobs", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ item }),
      });

      if (!response.ok) {
        throw new Error(`Error stopping solvers: ${response.statusText}`);
      }
    } catch (error) {
      console.error("Error stopping solvers:", error);
    }
  };

  const fetchDataGet = async () => {
    try {
      const response = await fetch("/api/solvers/mzn", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      const updatedData = data.map((item: MznSolverData) => ({
        ...item,
        solverIdentifier: uuidv4(),
      }));
      setMznSolverList(updatedData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleitemclick = (item: MznSolverData) => {
    if (selectedMznSolvers.find((i : any) => i.name === item.name)) {
      setSelectedMznSolvers((prevItems : Array<MznSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );
    } else {
      setSelectedMznSolvers((prevItems: Array<MznSolverData>) => [...prevItems, item]);
    }
  };

  const handlestartsolvers = () => {
    setRunningMznJobs(selectedMznSolvers);
    selectedMznSolvers.forEach(fetchstartsolvers);
    setSelectedMznSolvers([]);
    setMznSolverList((prevList) =>
      prevList.map((item) => ({
        ...item,
        solverIdentifier: uuidv4(),
      }))
    );

  };

  const fetchstartsolvers = async (item: MznSolverData) => {
    try {
      const response = await fetch("/api/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ item, mznFileContent, instructions: "StartMznJob" }),
      });

      let updateditem = await response.json();
      if (!response.ok) {
        updateditem = {
          ...item,
          solverIdentifier: uuidv4(),
          result: "Error starting solver",
          executionTime: 0,
          stopped: true,
        };
        throw new Error(`Error starting solvers: ${response.statusText}`);
      }
      if (updateditem !== "Solver stopped") {
        setMznJobResultList((prevItems: MznJobResult[]) => [
          ...prevItems,
          {
            name: item.name,
            solverIdentifier: uuidv4(),
            result: updateditem.result,
            executionTime: updateditem.executionTime,
            mznIdentifier: item.mznIdentifier,
          },
        ]);
      }

      // Update state here
      setRunningMznJobs((prevItems : Array<MznSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );
    } catch (error) {
      console.error("Error starting solvers:", error);
      return {
        ...item,
        result: "Error starting solver",
        executionTime: 0,
        stopped: true,
      };
    }
  };

  const handlefilechange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setMznFileContent(reader.result as string);
      };
      reader.readAsText(file);
    }
  };

  return (
    <>
      <h1>Solveploy</h1>
      <div>
        <input onChange={handlefilechange} type="file" />
      </div>
      <br />
      <h2>Available Solvers</h2>
      <div className="grid">
        {mznSolverList.map((item, index) => (
          <div
            key={index}
            className={`solver-item ${
              selectedMznSolvers.includes(item) ? "selected" : ""
            }`}
            onClick={() => handleitemclick(item)}
          >
            <div>Name: {item.name}</div>
            <div>MZN ID: {item.mznIdentifier}</div>
            <div>Solver ID: {item.solverIdentifier}</div>
          </div>
        ))}
      </div>
      <br />
      <button onClick={handlestartsolvers}>Start Solvers</button>
      <br />
      <div>
        <h2>Solver Results</h2>
        <div className="grid">
          {runningMznJobs.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              <div>Solver ID: {item.solverIdentifier}</div>
              <div>Waiting for result</div>
              <button onClick={() => fetchStopJob(item)}>
                Stop Solver
              </button>
            </div>
          ))}
          {mznJobResultList.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              <div>Solver ID: {item.solverIdentifier}</div>
              <div>Result: {item.result}</div>
              <div>Execution Time: {item.executionTime}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default Mzn;
