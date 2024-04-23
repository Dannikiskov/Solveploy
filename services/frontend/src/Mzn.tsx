import { useState } from "react";
import { useEffect } from "react";
import { v4 as uuidv4 } from "uuid";

import "./App.css";

interface MznSolverData {
  name: string;
  version: string;
  jobIdentifier: string;
  cpu?: number;
  memory?: number;
  params?: string; 
}

interface MznJobResult extends MznSolverData {
  result: string;
  executionTime: number;
  status: string;
  optValue: number;
}

function Mzn() {
  const [mznSolverList, setMznSolverList] = useState<MznSolverData[]>([]);
  const [selectedMznSolvers, setSelectedMznSolvers] = useState<MznSolverData[]>(
    []
  );
  const [expanded, setExpanded] = useState(false);
  const [dznOrJson, setDznOrJson] = useState<string>("dzn");
  const [t, setT] = useState<number>(0);
  const [k, setK] = useState<number>(0);
  const [mznFileContent, setMznFileContent] = useState<string>("");
  const [dataFileContent, setDataFileContent] = useState<string>("");
  const [runningMznJobs, setRunningMznJobs] = useState<MznSolverData[]>([]);
  const [optVal, setOptVal] = useState<string>("");
  const [bestResult, setBestResult] = useState<MznJobResult | null>(null);
  const [optGoal, setOptGoal] = useState<string>("");

  useEffect(() => {
    console.log("Hello from Mzn component");
    console.log("runningMznJobs:", runningMznJobs);
    const fetchResult = async () => {

        try {
          const response = await fetch("/api/results/mzn", {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          });
          if (!response.ok) {
            console.error("HALA HALA Error fetching results:", response.statusText);
            return; // Exit early if response is not OK
          }
          const data = await response.json() as MznJobResult
          console.log("BestResukt", bestResult)
          console.log("DATATDATADATA", data)
          if (bestResult == null || (optGoal === "minimize" && data.optValue < bestResult.optValue) || (optGoal === "maximize" && data.optValue > bestResult.optValue)) {
            setBestResult(data);
          }
        } catch (error) {
          console.error("Error fetching results:", error);
        }

    };
  
    // Fetch data initially
    fetchResult();
  
    // Fetch data every second
    const interval = setInterval(fetchResult, 5000);
  
    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, [selectedMznSolvers, runningMznJobs, bestResult, optGoal]);
  
  useEffect(() => {
    fetchDataGet();
  }, []);

  const fetchStopJob = async (item: MznSolverData) => {
    setRunningMznJobs((prevItems: Array<MznSolverData>) =>
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
        jobIdentifier: uuidv4().slice(0, 8),
        cpu: 0,
        memory: 0,
      }));
      setMznSolverList(updatedData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleitemclick = (item: MznSolverData) => {
    if (selectedMznSolvers.find((i: any) => i.name === item.name)) {
      setSelectedMznSolvers((prevItems: Array<MznSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );
    } else {
      setSelectedMznSolvers((prevItems: Array<MznSolverData>) => [
        ...prevItems,
        item,
      ]);
    }
    console.log(selectedMznSolvers);
  };

  const handlestartsolvers = () => {
    setBestResult(null);
    setRunningMznJobs(selectedMznSolvers);
    selectedMznSolvers.forEach(fetchstartsolvers);
    setSelectedMznSolvers([]);
    setMznSolverList((prevList) =>
      prevList.map((item) => ({
        ...item,
        jobIdentifier: uuidv4().slice(0, 8),
      }))
    );
  };

  const updateItemCpu = (item: MznSolverData, cpu: number) => {
    setMznSolverList((prevList) =>
      prevList.map((prevItem) =>
        prevItem.name === item.name ? { ...prevItem, cpu } : prevItem
      )
    );
    console.log(item.cpu)
  }

  const updateItemMemory = (item: MznSolverData, memory: number) => {
    setMznSolverList((prevList) =>
      prevList.map((prevItem) =>
        prevItem.name === item.name ? { ...prevItem, memory } : prevItem
      )
    );
    console.log(item.memory);
  }

  const updateItemParams = (event: React.ChangeEvent<HTMLInputElement>, item: MznSolverData) => {
      const file = event.target.files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = () => {
          const fileContent = reader.result as string;
          setMznSolverList((prevList) =>
            prevList.map((prevItem) =>
              prevItem.name === item.name ? { ...prevItem, params: fileContent } : prevItem
            )
          );
        };
        reader.readAsText(file);
      }
      console.log(item.params);
  }

  const updateOptVal = (s : string) => {
    setOptVal(s);
  }

  const fetchstartsolvers = async (item: MznSolverData) => {
    try {
      const response = await fetch("/api/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          item,
          mznFileContent,
          dataFileContent,
          dataFileType: dznOrJson,
          instructions: "StartMznJob",
          optVal: optVal,
        }),
      });

      const data = await response.json() as any;
      console.log(data);
      // Remove the item from runningMznSolvers list
      setRunningMznJobs((prevItems: Array<MznSolverData>) =>
        prevItems.filter((i) => i.name !== item.name)
      );
      if (data.status == "OPTIMAL_SOLUTION" || (data.status == "SATISFIED" && optGoal === "solve")) {
        stopAllSolvers();
      }

    } catch (error) {
      console.error("Error starting solvers:", error);
    }
  }


  const handleMznFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        const fileContent = reader.result as string;
        setMznFileContent(fileContent);
        if (fileContent.includes("solve minimize")){
          setOptGoal("minimize");
        }
        else if (fileContent.includes("solve maximize")){
          setOptGoal("maximize");
        }
        else if (fileContent.includes("solve satisfy")){
          setOptGoal("solve");
        }
      };
      reader.readAsText(file);
    }
  };


  const handleDataFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      console.log("File name:", file.name);
      if(file.name.endsWith(".json")){
        setDznOrJson(".json");
      }
      else{
        setDznOrJson(".dzn");
      }
      const reader = new FileReader();
      reader.onload = () => {
      setDataFileContent(reader.result as string);
      };
      reader.readAsText(file);
    }

  };


  const stopAllSolvers = async () => {
    try {
      const response = await fetch("/api/jobs", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) {
        console.error("Error stopping all solvers:", response.statusText);
      }
    } catch (error) {
      console.error("Error stopping all solvers:", error);
    }
  };


  async function startSunny(): Promise<any> {
    console.log("Starting SUNNY");
    console.log("k: ", k);
    console.log("T: ", t);
    console.log("solvers:", selectedMznSolvers);
    const response = await fetch("/api/jobs/sunny", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        k,
        T: t,
        solvers: selectedMznSolvers,
        backupSolver: selectedMznSolvers[selectedMznSolvers.length - 1],
        fileContent: mznFileContent,
        solverType: "mzn",
      }),
    });
    if (!response.ok) {
      console.error("Error starting SUNNY:", response.statusText);
    }
    console.log("SUNNY started");
    setSelectedMznSolvers([]);
    let responeAsJson = await response.json();
    console.log(responeAsJson);
  }

  return (
    <>
    <br />
    <h2>Upload Files</h2>
      <div>
        <h3>Upload MZN file</h3>
        <input onChange={handleMznFileChange} type="file" />
      </div>
      <br></br>
      <div>
        <h3>Upload Data file</h3>
        <input onChange={handleDataFileChange} type="file" />
      </div>
      <br />
      <button onClick={() => setExpanded(!expanded)}>SUNNY</button>
      <br />
      {expanded && (
        <div>
          Last chosen solver is backup solver.
          <br />
          <input
            type="text"
            placeholder="k"
            onChange={(e) => setK(Number(e.target.value))}
          />
          <br />
          <input
            type="text"
            placeholder="T"
            onChange={(e) => setT(Number(e.target.value))}
          />
          <br />
          <button onClick={startSunny}>Get SUNNY portfolio</button>
        </div>
        
      )}
      <div>
        <input
          type="string"
          placeholder="Optimization value"
          onChange={(e) => {updateOptVal(e.target.value)}}
        />
      </div>
      <br />
      <h2>Available Solvers</h2>
      <div className="grid">
        {mznSolverList.map((item, index) => (
          <div
            key={index}
            className={`solver-item ${
              selectedMznSolvers.find((i) => i.name === item.name) ? "selected" : ""
            }`}
          >
            <div>Name: {item.name}</div>
            <div>Version: {item.version}</div>
            <div>
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
            </div>
            <br />
            <input onChange={(e) => {updateItemParams(e, item)}} type="file" />
            <br />
            <button className="small-button" onClick={() => handleitemclick(item)}>Select</button>
          </div>
          
        ))}
      </div>
      <br />
      <button onClick={handlestartsolvers}>Start Solvers</button>
      <br />
      <div>
        <h2>Running Solvers</h2>
        <div className="grid">
          {runningMznJobs.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              <button className="small-button" onClick={() => fetchStopJob(item)}>Stop Solver</button>
            </div>
          ))}
          
        </div>
        <br />
        <h2>Result</h2>
        <div>    
          {bestResult && (
            <div className="result-container">
              <h4>Solver Information</h4>
              <div>Name: {bestResult.name}</div>
              <div>Version: {bestResult.version}</div>
              <h4>Output</h4>
              <div>Status: {bestResult.status}</div>
              <div>Execution Time: {bestResult.executionTime} milliseconds</div>
              <div>Result: {bestResult.result}</div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default Mzn;




