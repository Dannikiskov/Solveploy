import { useState } from "react";
import { useEffect } from "react";
import { v4 as uuidv4 } from "uuid";

import "./App.css";

interface MaxsatSolverData {
  name: string;
  maxsatIdentifier: string;
  jobIdentifier: string;
}

interface MaxsatJobResult extends MaxsatSolverData {
  result: string;
  executionTime: number;
}

function Maxsat() {
  const [maxsatSolverList, setMaxsatSolverList] = useState<MaxsatSolverData[]>(
    []
  );
  const [selectedMaxsatSolvers, setSelectedMaxsatSolvers] = useState<
    MaxsatSolverData[]
  >([]);
  const [cnfFileContent, setCnfFileContent] = useState<string>("");
  const [runningMaxsatJobs, setRunningMaxsatJobs] = useState<
    MaxsatSolverData[]
  >([]);
  const [maxsatJobResultList, setMaxsatJobResultList] = useState<
    MaxsatJobResult[]
  >([]);

  useEffect(() => {
    fetchDataGet();
  }, []);

  const fetchStopJob = async (item: MaxsatSolverData) => {
    setRunningMaxsatJobs((prevItems: Array<MaxsatSolverData>) =>
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
      const response = await fetch("/api/solvers/maxsat", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      const updatedData = data.map((item: MaxsatSolverData) => ({
        ...item,
        jobIdentifier: uuidv4().slice(0, 8),
      }));
      setMaxsatSolverList(updatedData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleitemclick = (item: MaxsatSolverData) => {
    if (selectedMaxsatSolvers.find((i: any) => i.name === item.name)) {
      setSelectedMaxsatSolvers((prevItems: Array<MaxsatSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );
    } else {
      setSelectedMaxsatSolvers((prevItems: Array<MaxsatSolverData>) => [
        ...prevItems,
        item,
      ]);
    }
  };

  const handlestartsolvers = () => {
    setRunningMaxsatJobs(selectedMaxsatSolvers);
    selectedMaxsatSolvers.forEach(fetchstartsolvers);
    setSelectedMaxsatSolvers([]);
    setMaxsatSolverList((prevList) =>
      prevList.map((item) => ({
        ...item,
        jobIdentifier: uuidv4().slice(0, 8),
      }))
    );
  };

  const fetchstartsolvers = async (item: MaxsatSolverData) => {
    try {
      const response = await fetch("/api/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          item,
          cnfFileContent,
          instructions: "StartMaxsatJob",
        }),
      });

      let updateditem = await response.json();
      if (!response.ok) {
        updateditem = {
          ...item,
          jobIdentifier: uuidv4().slice(0, 8),
          result: "Error starting solver",
          executionTime: 0,
          stopped: true,
        };
        throw new Error(`Error starting solvers: ${response.statusText}`);
      }
      if (updateditem !== "Solver stopped") {
        setMaxsatJobResultList((prevItems: MaxsatJobResult[]) => [
          ...prevItems,
          {
            name: item.name,
            jobIdentifier: uuidv4().slice(0, 8),
            result: updateditem.result,
            executionTime: updateditem.executionTime,
            maxsatIdentifier: item.maxsatIdentifier,
          },
        ]);
      }

      // Update state here
      setRunningMaxsatJobs((prevItems: Array<MaxsatSolverData>) =>
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
        setCnfFileContent(reader.result as string);
        console.log(reader.result);
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
        {maxsatSolverList.map((item, index) => (
          <div
            key={index}
            className={`solver-item ${
              selectedMaxsatSolvers.includes(item) ? "selected" : ""
            }`}
            onClick={() => handleitemclick(item)}
          >
            <div>Name: {item.name}</div>
            <div>MAXSAT ID: {item.maxsatIdentifier}</div>
            <div>Job ID: {item.jobIdentifier}</div>
          </div>
        ))}
      </div>
      <br />
      <button onClick={handlestartsolvers}>Start Solvers</button>
      <br />
      <div>
        <h2>Solver Results</h2>
        <div className="grid">
          {runningMaxsatJobs.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              <div>Job ID: {item.jobIdentifier}</div>
              <div>Waiting for result</div>
              <button onClick={() => fetchStopJob(item)}>Stop Solver</button>
            </div>
          ))}
          {maxsatJobResultList.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              <div>Job ID: {item.jobIdentifier}</div>
              <div>Result: {item.result}</div>
              <div>Execution Time: {item.executionTime}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default Maxsat;
