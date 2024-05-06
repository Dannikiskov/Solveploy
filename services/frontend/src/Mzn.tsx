import { useState } from "react";
import { useEffect } from "react";
import { v4 as uuidv4 } from "uuid";;
import "./App.css";
import React from "react";

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
  executionTime?: number;
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
  const [folderMapping, setFolderMapping] = useState<{ [key: string]: { mzn: { file: File, content: string } | null, dzn: { file: File, content: string } | null } }>({});
  // useEffect(() => {
  //   // console.log("Hello from Mzn component");
  //   // console.log("runningMznJobs:", runningMznJobs);
  //   const fetchResult = async () => {

  //       try {
  //         const response = await fetch("/api/results/mzn", {
  //           method: "GET",
  //           headers: {
  //             "Content-Type": "application/json",
  //           },
  //         });
  //         if (!response.ok) {
  //           console.error("HALA HALA Error fetching results:", response.statusText);
  //           return; // Exit early if response is not OK
  //         }
  //         const data = await response.json() as MznJobResult;

  //         console.log("\n----NEW---\n");
  //         console.log("DATA", data);
  //         console.log("BESTRESULT", bestResult);
  //         console.log("\n----\n");
  //         if (data ==  null){
  //           return;
  //         }

  //         else if (bestSet === false){
  //           setBestResult(data);
  //           setBestSet(true);
  //         }
  //         else if (optGoal === "minimize" && data.optValue < (bestResult?.optValue ?? 0)){
  //           setBestResult(data);
  //         }
  //         else if (optGoal === "maximize" && data.optValue > (bestResult?.optValue ?? 0)){
  //           setBestResult(data);
  //         }
  //         else if (bestResult && data.status === bestResult.status){
  //           if (data.executionTime != null && data.executionTime < (bestResult?.executionTime ?? 0)){
  //             setBestResult(data);
  //           }
  //         }
          
  //       } catch (error) {
  //         console.error("Error fetching results:", error);
  //       }

  //   };
  
  //   // Fetch data initially
  //   fetchResult();
  
  //   // Fetch data every second
  //   const interval = setInterval(fetchResult, 5000);
  
  //   // Cleanup interval on unmount
  //   return () => clearInterval(interval);
  // }, []);
  
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

  const handleItemClick = (item: MznSolverData) => {
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
    //console.log(selectedMznSolvers);
  };

  const handleStartSolvers = () => {
    setBestResult(null);
    setRunningMznJobs(selectedMznSolvers);
    selectedMznSolvers.forEach(fetchStartSolvers);
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

  const fetchStartSolvers = async (item: MznSolverData) => {
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
      //console.log(data);
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

  const fetchStartSolverWithContent = (item: MznSolverData, mznString: string, dataString: string, suffix: string) => {
    const updatedItem = {
      ...item,
      jobIdentifier: uuidv4().slice(0, 8),
    };

    fetch("/api/jobs", {
      method: "POST",
      headers: {
      "Content-Type": "application/json",
      },
      
      body: JSON.stringify({
      item: updatedItem,
      mznFileContent : mznString,
      dataFileContent: dataString,
      dataFileType: suffix,
      instructions: "StartMznJob",
      optVal: optVal,
      }),
    }).catch(error => {
      console.error("Error starting solvers:", error);
    });
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
      // console.log("File name:", file.name);
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
        dataContent: dataFileContent,
        dataFileType: dznOrJson,
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

  const handleFolderChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileMapping: { [key: string]: { mzn: { file: File, content: string } | null, dzn: { file: File, content: string } | null } } = {};
  
      for (let i = 0; i < e.target.files.length; i++) {
        const file = e.target.files[i] as any;
        const pathParts = file.webkitRelativePath.split('/');
        const folder = pathParts[pathParts.length - 2]; // Get the parent folder name
  
        if (!fileMapping[folder]) {
          fileMapping[folder] = { mzn: null, dzn: null };
        }
  
        const fileContent = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = event => resolve(event.target?.result as string);
          reader.onerror = error => reject(error);
          reader.readAsText(file);
        });
  
        if (file.name.endsWith('.mzn')) {
          fileMapping[folder].mzn = { file, content: fileContent };
        } else if (file.name.endsWith('.dzn')) {
          fileMapping[folder].dzn = { file, content: fileContent };
        }
      }
  
      // console.log(fileMapping);
      setFolderMapping(fileMapping);
    }
  }

  const startSolverWithAllFiles = async () => {
    for (const solver of selectedMznSolvers) {
      for (const folder in folderMapping) {
        const { mzn, dzn } = folderMapping[folder];
        if (mzn && dzn) {
          setOptVal("");
          await fetchStartSolverWithContent(solver, mzn.content, dzn.content, dzn.file.name.endsWith('.json') ? '.json' : '.dzn');
        }
        else if (mzn && !dzn) {
          setOptVal("");
          await fetchStartSolverWithContent(solver, mzn.content, "", "");
        }
      }
    }
  }

  async function handleRefresh(): Promise<void> {
    try {
      const response = await fetch("/api/results", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          item: bestResult,
          type: "mzn",
          optGoal
        }),
      });
      if (!response.ok) {
        console.error("Error fetching results:", response.statusText);
        return; // Exit early if response is not OK
      }
      const data = await response.json() as MznJobResult;
      console.log("DATA", data);
      if (data != null){
        setBestResult(data);
      }
      
      
    } catch (error) {
      console.error("Error fetching results:", error);
    }

  }

  return (
    <>
    <br />
    <h2>Upload Files</h2>
      <div className="result-container">
        <div>
          <h3>Upload MZN file</h3>
          <input onChange={handleMznFileChange} type="file" />
        </div>
        <br></br>
        <div>
          <h3>Upload Data file</h3>
          <input onChange={handleDataFileChange} type="file" />
        </div>
      </div>
      <div className="result-container">
        <h3>Upload folder</h3>
        {React.createElement('input', {
          type: 'file',
          webkitdirectory: '',
          mozdirectory: '',
          directory: '',
          onChange: handleFolderChange
        })}
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
      <div className="result-container">
        <br />
        <h4>Optimization value</h4>
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
            <button className="small-button" onClick={() => handleItemClick(item)}>Select</button>
          </div>
          
        ))}
      </div>
      <br />
      <div className="result-container">
        <button onClick={startSolverWithAllFiles}>Start Solvers with all files</button>
      </div>
      <br />
      <button onClick={handleStartSolvers}>Start Solvers</button>
      <br />
      <div className="result-container">
        <h2>Running Solvers</h2>
        <div className="grid">
          {runningMznJobs.map((item, index) => (
            <div key={index} className="solver-item">
              <div>Name: {item.name}</div>
              <button className="small-button" onClick={() => fetchStopJob(item)}>Stop Solver</button>
            </div>
          ))}
          
        </div>
        </div>
        <div>
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
        <div>
          <button onClick={handleRefresh}>Refresh Result</button>
        </div>
      </div>
    </>
  );
}

export default Mzn;




