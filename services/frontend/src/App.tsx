import { useState } from "react";
import { useEffect } from "react";
import { v4 as uuidv4 } from "uuid";

import "./App.css";

interface SolverData {
  name: string;
  mznIdentifier: string;
  solverIdentifier: string;
}

interface JobResult extends SolverData {
  result: string;
  executionTime: number;
}

function App() {
  const [solverList, setSolverList] = useState<SolverData[]>([]);
  const [selectedSolvers, setSelectedSolvers] = useState<SolverData[]>([]);
  const [mznFileContent, setMznFileContent] = useState<string>("");
  const [runningJobs, setRunningJobs] = useState<SolverData[]>([]);
  const [jobResultList, setJobResultList] = useState<
    JobResult[]
  >([]);

  useEffect(() => {
    fetchDataGet();
  }, []);

  const fetchStopJob = async (item: SolverData) => {
    setRunningJobs((prevItems : Array<SolverData>) =>
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
      const response = await fetch("/api/knowledgebase/solvers", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      const updatedData = data.map((item: SolverData) => ({
        ...item,
        solverIdentifier: uuidv4(),
      }));
      setSolverList(updatedData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleitemclick = (item: SolverData) => {
    if (selectedSolvers.find((i : any) => i.name === item.name)) {
      setSelectedSolvers((prevItems : Array<SolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );
    } else {
      setSelectedSolvers((prevItems: Array<SolverData>) => [...prevItems, item]);
    }
  };

  const handlestartsolvers = () => {
    setRunningJobs(selectedSolvers);
    selectedSolvers.forEach(fetchstartsolvers);
  };

  const fetchstartsolvers = async (item: SolverData) => {
    try {
      const response = await fetch("/api/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ item, mznFileContent }),
      });

      let updateditem = await response.json();
      if (!response.ok) {
        updateditem = {
          ...item,
          result: "Error starting solver",
          executionTime: 0,
          stopped: true,
        };
        throw new Error(`Error starting solvers: ${response.statusText}`);
      }
      if (updateditem !== "Solver stopped") {
        setJobResultList((prevItems: JobResult[]) => [
          ...prevItems,
          {
            name: item.name,
            solverIdentifier: item.solverIdentifier,
            result: updateditem.result,
            executionTime: updateditem.executionTime,
            mznIdentifier: item.mznIdentifier,
          },
        ]);
      }

      // Update state here
      setRunningJobs((prevItems : Array<SolverData>) =>
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
        {solverList.map((item, index) => (
          <div
            key={index}
            className={`solver-item ${
              selectedSolvers.includes(item) ? "selected" : ""
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
          {runningJobs.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              <div>Solver ID: {item.solverIdentifier}</div>
              <div>Waiting for result</div>
              <button onClick={() => fetchStopJob(item)}>
                Stop Solver
              </button>
            </div>
          ))}
          {jobResultList.map((item, index) => (
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

export default App;
