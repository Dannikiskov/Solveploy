import { useState } from "react";
import { useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import { saveAs } from 'file-saver';

import "./App.css";

interface MaxsatSolverData {
  name: string;
  maxsatIdentifier: string;
  jobIdentifier: string;
  cpu?: number;
  memory?: number;
}
interface MaxsatJobResult extends MaxsatSolverData {
  result: string;
  executionTime?: number;
  status: string;
  optValue: number;
}

function Maxsat() {
  const [maxsatSolverList, setMaxsatSolverList] = useState<MaxsatSolverData[]>(
    []
  );
  const [bestResult, setBestResult] = useState<MaxsatJobResult | null>(null);
  const [selectedMaxsatSolvers, setSelectedMaxsatSolvers] = useState<
    MaxsatSolverData[]
  >([]);
  const [maxsatFileContent, setMaxsatFileContent] = useState<string>("");
  const [maxsatFileName, setMaxsatFileName] = useState<string>("");
  const [runningMaxsatJobs, setRunningMaxsatJobs] = useState<
    MaxsatSolverData[]
  >([]);

  useEffect(() => {
    fetchDataGet();
  }, []);

  const updateItemMemory = (item: MaxsatSolverData, memory: number) => {
    setMaxsatSolverList((prevList) =>
      prevList.map((prevItem) =>
        prevItem.name === item.name ? { ...prevItem, memory } : prevItem
      )
    );
    console.log(item.memory);
  }

  const updateItemCpu = (item: MaxsatSolverData, cpu: number) => {
    setMaxsatSolverList((prevList) =>
      prevList.map((prevItem) =>
        prevItem.name === item.name ? { ...prevItem, cpu } : prevItem
      )
    );
    console.log(item.cpu)
  }

  const downloadResult = () => {
    if (!bestResult) return;
  
    const content = `Solver Information
Name: ${bestResult.name}
Output
Status: ${bestResult.status}
Execution Time: ${bestResult.executionTime} seconds
Result: 
${bestResult.result}
    `;
  
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    saveAs(blob, 'result.txt');
  };


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

  async function handleRefresh(): Promise<void> {
    try {
      const response = await fetch("/api/results", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          item: bestResult,
          type: "maxsat",
          optGoal: "satisfy",
        }),
      });
      if (!response.ok) {
        console.error("Error fetching results:", response.statusText);
        return; // Exit early if response is not OK
      }
      const data = await response.json() as MaxsatJobResult;
      console.log("DATA", data);
      if (data != null){
        setBestResult(data);
      }
      
      
    } catch (error) {
      console.error("Error fetching results:", error);
    }
  }

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

  const handlestartsolvers = () => {
    setRunningMaxsatJobs(selectedMaxsatSolvers);
    selectedMaxsatSolvers.forEach(fetchStartSolvers);
    setSelectedMaxsatSolvers([]);
    setMaxsatSolverList((prevList) =>
      prevList.map((item) => ({
        ...item,
        jobIdentifier: uuidv4().slice(0, 8),
      }))
    );
  };

  const handleItemClick = (item: MaxsatSolverData) => {
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
    //console.log(selectedSatSolvers);
  };
  

  const fetchStartSolvers = async (item: MaxsatSolverData) => {
    try {
      const response = await fetch("/api/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          item,
          maxsatFileContent,
          maxsatFileName,
          instructions: "StartSatJob",
          optGoal: "satisfy",
        }),
      });


      console.log(response);
      // Remove the item from runningSatSolvers list
      setRunningMaxsatJobs((prevItems: Array<MaxsatSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );

    } catch (error) {
      console.error("Error starting solvers:", error);
    }
  }

  const handlefilechange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setMaxsatFileName(file.name);
      const reader = new FileReader();
      reader.onload = () => {
        setMaxsatFileContent(reader.result as string);
        console.log(reader.result);
      };
      reader.readAsText(file);
    }
  };

  return (
    <>
      <div>
      <h3>Upload CNF file</h3>
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
          >
            <div>Name: {item.name}</div>
            <input
                type="number"
                placeholder="CPU"
                onChange={(e) => {updateItemCpu(item, Number(e.target.value))}}
              />
              <br />
              <input
                type="number"
                placeholder="Memory"
                onChange={(e) => {updateItemMemory(item, Number(e.target.value))}}
              />
              <br />
              <button className="small-button" onClick={() => handleItemClick(item)} disabled={!item.memory || !item.cpu}>Select</button>
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
      <h2>Result</h2>
        <div>    
          {bestResult && (
            <div className="result-container">
              <h4>Solver Information</h4>
              <div>Name: {bestResult.name}</div>
              <h4>Output</h4>
              <div>Status: {bestResult.status}</div>
              <div>Execution Time: {bestResult.executionTime} seconds</div>
              <div>Result: {bestResult.result}</div>
              <br />
              <button onClick={downloadResult}>Download Result</button>
            </div>
          )}
        </div>
        <div style={{ marginBottom: '20px' }}>
          <button onClick={handleRefresh}>Refresh Result</button>
        </div>
        </div>
      </div>
    </>
  );
}

export default Maxsat;
