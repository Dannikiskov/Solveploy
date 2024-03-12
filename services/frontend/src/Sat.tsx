import { useState } from "react";
import { useEffect } from "react";
import { v4 as uuidv4 } from "uuid";

import "./App.css";

interface SatSolverData {
  name: string;
  satIdentifier: string;
  jobIdentifier: string;
}

interface SatJobResult extends SatSolverData {
  result: string;
  executionTime: number;
}

function Sat() {
  const [satSolverList, setSatSolverList] = useState<SatSolverData[]>([]);
  const [selectedSatSolvers, setSelectedSatSolvers] = useState<SatSolverData[]>(
    []
  );
  const [cnfFileContent, setCnfFileContent] = useState<string>("");
  const [runningSatJobs, setRunningSatJobs] = useState<SatSolverData[]>([]);
  const [satJobResultList, setSatJobResultList] = useState<SatJobResult[]>([]);

  useEffect(() => {
    fetchDataGet();
  }, []);

  const fetchStopJob = async (item: SatSolverData) => {
    setRunningSatJobs((prevItems: Array<SatSolverData>) =>
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
      const response = await fetch("/api/solvers/sat", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      const updatedData = data.map((item: SatSolverData) => ({
        ...item,
        jobIdentifier: uuidv4().slice(0, 8),
      }));
      setSatSolverList(updatedData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleitemclick = (item: SatSolverData) => {
    if (selectedSatSolvers.find((i: any) => i.name === item.name)) {
      setSelectedSatSolvers((prevItems: Array<SatSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );
    } else {
      setSelectedSatSolvers((prevItems: Array<SatSolverData>) => [
        ...prevItems,
        item,
      ]);
    }
  };

  const handlestartsolvers = () => {
    setRunningSatJobs(selectedSatSolvers);
    selectedSatSolvers.forEach(fetchstartsolvers);
    setSelectedSatSolvers([]);
    setSatSolverList((prevList) =>
      prevList.map((item) => ({
        ...item,
        jobIdentifier: uuidv4().slice(0, 8),
      }))
    );
  };

  const fetchstartsolvers = async (item: SatSolverData) => {
    try {
      const response = await fetch("/api/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          item,
          cnfFileContent,
          instructions: "StartSatJob",
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
        setSatJobResultList((prevItems: SatJobResult[]) => [
          ...prevItems,
          {
            name: item.name,
            jobIdentifier: uuidv4().slice(0, 8),
            result: updateditem.result,
            executionTime: updateditem.executionTime,
            satIdentifier: item.satIdentifier,
          },
        ]);
      }

      // Update state here
      setRunningSatJobs((prevItems: Array<SatSolverData>) =>
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
        {satSolverList.map((item, index) => (
          <div
            key={index}
            className={`solver-item ${
              selectedSatSolvers.includes(item) ? "selected" : ""
            }`}
            onClick={() => handleitemclick(item)}
          >
            <div>Name: {item.name}</div>
            <div>SAT ID: {item.satIdentifier}</div>
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
          {runningSatJobs.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              <div>Job ID: {item.jobIdentifier}</div>
              <div>Waiting for result</div>
              <button onClick={() => fetchStopJob(item)}>Stop Solver</button>
            </div>
          ))}
          {satJobResultList.map((item, index) => (
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

export default Sat;
