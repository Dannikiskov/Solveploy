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
  const [mznJobResultList, setMznJobResultList] = useState<MznJobResult[]>([]);
  const [optVal, setOptVal] = useState<string>("");

  useEffect(() => {
    fetchDataGet();
  }, []);

  useEffect(() => {

      console.log(  selectedMznSolvers);

  }, [selectedMznSolvers]);

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
  };

  const handlestartsolvers = () => {
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
        setMznJobResultList((prevItems: MznJobResult[]) => [
          ...prevItems,
          {
            name: item.name,
            jobIdentifier: uuidv4().slice(0, 8),
            result: updateditem.result,
            executionTime: updateditem.executionTime,
            version: item.version,
            status: updateditem.status,
          },
        ]);
      }

      setRunningMznJobs([]);
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

  const handleMznFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setMznFileContent(reader.result as string);
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
          <div>
          <br />
          <input
                type="string"
                placeholder="Optimization value"
                onChange={(e) => {updateOptVal(e.target.value)}}
              />
          </div>
        </div>
        
      )}
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
              <input
                type="number"
                placeholder="Memory"
                onChange={(e) => {updateItemMemory(item, Number(e.target.value))}}
              />
            </div>
            <input onChange={(e) => {updateItemParams(e, item)}} type="file" />
            <button className="small-button" onClick={() => handleitemclick(item)}>Select</button>
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
              <div>Waiting for result</div>
              <button onClick={() => fetchStopJob(item)}>Stop Solver</button>
            </div>
          ))}
          {mznJobResultList.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              <div>Result: {item.result}</div>
              <div>Execution Time: {item.executionTime} milliseconds</div>
              <div>Status: {item.status}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default Mzn;
